from fastapi import APIRouter, Request
from firebase_admin import auth as firebase_auth

router = APIRouter()

@router.post("/test-auth")
async def test_auth(request: Request):
    """Test endpoint to debug authentication"""
    headers = dict(request.headers)
    auth_header = headers.get('authorization', 'NOT FOUND')
    
    print(f"All headers: {headers}")
    print(f"Authorization header: {auth_header}")
    
    if auth_header and auth_header != 'NOT FOUND':
        try:
            # Extract token (remove 'Bearer ' prefix if present)
            token = auth_header.replace('Bearer ', '').replace('bearer ', '')
            print(f"Extracted token: {token[:50]}...")
            
            # Try to verify with Firebase
            decoded = firebase_auth.verify_id_token(token)
            print(f"Token verified! User: {decoded.get('email')}")
            
            return {
                "status": "success",
                "message": "Token verified successfully",
                "user": decoded.get('email'),
                "uid": decoded.get('uid')
            }
        except Exception as e:
            print(f"Verification failed: {type(e).__name__}: {str(e)}")
            return {
                "status": "error",
                "message": f"Token verification failed: {str(e)}",
                "token_preview": token[:50] if len(token) > 50 else token
            }
    else:
        return {
            "status": "error",
            "message": "No authorization header found",
            "headers": headers
        }
