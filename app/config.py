import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
X_TEST_PATH = os.path.join(DATA_DIR, "X_test.csv")
Y_TRUE_PATH = os.path.join(DATA_DIR, "y_true.csv")
FIREBASE_CREDENTIALS_PATH = os.path.join(DATA_DIR, "portal-11326-firebase-adminsdk-fbsvc-2cd1059886.json")

EVALUATION_TIMEOUT = 30
MAX_RETRIES = 2
QUEUE_CHECK_INTERVAL = 5

API_HOST = "0.0.0.0"
API_PORT = 8000

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS Configuration - Add your Vercel domain here
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if ALLOWED_ORIGINS == ["*"]:
    ALLOWED_ORIGINS = [
        "http://localhost:*",
        "http://127.0.0.1:*",
        "*"  # Allow all in development, restrict in production
    ]
