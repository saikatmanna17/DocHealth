from jose import jwt
from datetime import datetime, timedelta

SECRET = "MY_SECRET_KEY"

def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")