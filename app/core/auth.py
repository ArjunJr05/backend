from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from firebase_admin import auth as firebase_auth

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    uid: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    print(f"Received token: {token[:50]}..." if len(token) > 50 else f"Received token: {token}")
    
    try:
        # Verify Firebase ID token
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        print(f"Token verified successfully for user: {email} (uid: {uid})")
        
        if not uid or not email:
            print("Token missing uid or email")
            raise credentials_exception
            
        token_data = TokenData(email=email, uid=uid)
        return token_data
    except Exception as e:
        error_name = type(e).__name__
        print(f"Token verification error: {error_name}: {str(e)}")
        
        # Development mode: Allow requests when Firebase is unreachable
        if "CertificateFetchError" in error_name or "ConnectionError" in error_name or "NameResolutionError" in str(e):
            print("⚠️  Firebase unreachable - using development mode bypass")
            # Extract email from token payload without verification (DEV ONLY)
            import base64
            import json
            try:
                payload = token.split('.')[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload))
                email = decoded.get('email', 'dev@localhost')
                uid = decoded.get('user_id') or decoded.get('sub', 'dev_user')
                print(f"Development mode: Allowing user {email} (uid: {uid})")
                return TokenData(email=email, uid=uid)
            except:
                print("Development mode: Using default dev user")
                return TokenData(email="dev@localhost", uid="dev_user")
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Authentication failed: {str(e)}"
        )

async def create_user(email: str, password: str) -> dict:
    try:
        user = firebase_auth.create_user(
            email=email,
            password=password
        )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email, "uid": user.uid}, 
            expires_delta=access_token_expires
        )
        
        return {
            "uid": user.uid,
            "email": user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )

async def authenticate_user(email: str, password: str) -> dict:
    try:
        user = firebase_auth.get_user_by_email(email)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email, "uid": user.uid}, 
            expires_delta=access_token_expires
        )
        
        return {
            "uid": user.uid,
            "email": user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except firebase_auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error authenticating user: {str(e)}"
        )
