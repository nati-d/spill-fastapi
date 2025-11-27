import hmac
import hashlib
import time
import json
import logging
from core.config import settings

logger = logging.getLogger(__name__)

def validate_init_data(init_data: str) -> dict:
    """Validate Telegram init data and return the user data"""
    
    if not init_data or not init_data.strip():
        raise ValueError("init_data is empty or missing")

    from urllib.parse import parse_qs
    try:
        params = parse_qs(init_data)
    except Exception as e:
        raise ValueError(f"Failed to parse init_data: {str(e)}")

    if "hash" not in params:
        raise ValueError("hash not found in init data")
    
    hash_value = params.pop("hash")[0]
    data_check_string = "\n".join([f"{k}={v[0]}" for k, v in sorted(params.items())])

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_value:
        logger.warning(f"Hash mismatch. Expected: {calculated_hash}, Got: {hash_value}")
        raise ValueError("Invalid hash in init data - authentication failed")
    
    auth_date = params.get("auth_date", [None])[0]
    if not auth_date:
        raise ValueError("auth_date not found in init data")
    
    try:
        auth_timestamp = int(auth_date)
        if time.time() - auth_timestamp > 86400:
            raise ValueError("Auth date is more than 24 hours old")
    except ValueError as e:
        if "24 hours" in str(e):
            raise
        raise ValueError(f"Invalid auth_date format: {str(e)}")
    
    user_str = params.get("user", [None])[0]
    if not user_str:
        raise ValueError("User not found in init data")
    
    try:
        user_data = json.loads(user_str)
        if "id" not in user_data:
            raise ValueError("User ID not found in user data")
        return user_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse user data as JSON: {str(e)}")
    