from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "secret") # Fallback to "secret" for local testing if not set

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_SECRET_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
