import hmac
import hashlib
import time
import json
import logging
from urllib.parse import unquote
from core.config import settings

logger = logging.getLogger(__name__)

def validate_init_data(init_data: str) -> dict:
    """
    Validate Telegram init data and return the user data.
    
    According to Telegram docs, the hash must be calculated from the ORIGINAL
    URL-encoded query string values, not decoded ones.
    """
    
    if not init_data or not init_data.strip():
        raise ValueError("init_data is empty or missing")

    # Parse the query string manually to preserve original encoding
    params_dict = {}
    hash_value = None
    
    for pair in init_data.split('&'):
        if '=' not in pair:
            continue
        key, value = pair.split('=', 1)  # Split only on first '='
        if key == 'hash':
            hash_value = value
        else:
            # Store the original URL-encoded value for hash calculation
            if key not in params_dict:
                params_dict[key] = []
            params_dict[key].append(value)
    
    if not hash_value:
        raise ValueError("hash not found in init data")
    
    # Build data_check_string from ORIGINAL encoded values (not decoded)
    # Sort keys alphabetically and join as key=value with newlines
    data_check_string = "\n".join([
        f"{k}={v[0]}" for k, v in sorted(params_dict.items())
    ])
    
    # Calculate secret key from bot token
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_value:
        logger.warning(f"Hash mismatch. Expected: {calculated_hash}, Got: {hash_value}")
        logger.debug(f"Data check string: {data_check_string}")
        logger.debug(f"Bot token length: {len(settings.TELEGRAM_BOT_TOKEN)}")
        raise ValueError("Invalid hash in init data - authentication failed")
    
    # Now decode values for actual use
    auth_date = params_dict.get("auth_date", [None])[0]
    if not auth_date:
        raise ValueError("auth_date not found in init data")
    
    try:
        auth_timestamp = int(unquote(auth_date))
        if time.time() - auth_timestamp > 86400:
            raise ValueError("Auth date is more than 24 hours old")
    except ValueError as e:
        if "24 hours" in str(e):
            raise
        raise ValueError(f"Invalid auth_date format: {str(e)}")
    
    user_str = params_dict.get("user", [None])[0]
    if not user_str:
        raise ValueError("User not found in init data")
    
    try:
        # Decode the user JSON string
        user_data = json.loads(unquote(user_str))
        if "id" not in user_data:
            raise ValueError("User ID not found in user data")
        return user_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse user data as JSON: {str(e)}")
    