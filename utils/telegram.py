import hmac
import hashlib
import time
import json
import logging
from urllib.parse import unquote, quote
from core.config import settings

logger = logging.getLogger(__name__)

def validate_init_data(init_data: str) -> dict:
    """
    Validate Telegram init data and return the user data.
    
    According to Telegram docs:
    1. Parse query string and extract hash
    2. Sort all parameters (except hash) alphabetically
    3. Create data_check_string: key=value pairs joined by newlines
    4. Calculate HMAC-SHA256 using bot token as secret
    """
    
    if not init_data or not init_data.strip():
        raise ValueError("init_data is empty or missing")

    # Parse the query string - preserve original values as they come
    params_dict = {}
    hash_value = None
    
    # Handle both URL-encoded and already-decoded data
    for pair in init_data.split('&'):
        if '=' not in pair:
            continue
        key, value = pair.split('=', 1)  # Split only on first '='
        if key == 'hash':
            hash_value = value
        else:
            # Store the value as-is (might be encoded or decoded)
            if key not in params_dict:
                params_dict[key] = value
    
    if not hash_value:
        raise ValueError("hash not found in init data")
    
    # Build data_check_string: sort keys alphabetically, join as key=value with newlines
    # CRITICAL: Use values exactly as they appear in the original query string
    # If FastAPI decoded them, we need to detect and handle that
    data_check_parts = []
    for k in sorted(params_dict.keys()):
        v = params_dict[k]
        
        # Check if value appears to be already decoded (contains unencoded special chars)
        # If so, we need to re-encode it for hash calculation
        # Telegram's hash is calculated from URL-encoded values
        needs_encoding = False
        if '%' not in v:  # No existing encoding
            # Check for characters that should be encoded in URL
            if any(c in v for c in [' ', '{', '}', '[', ']', ':', ',', '"', '\'', '\\']):
                needs_encoding = True
        
        if needs_encoding:
            # Re-encode the value for hash calculation
            # Use quote with safe='' to encode everything except alphanumeric
            v = quote(v, safe='')
        
        data_check_parts.append(f"{k}={v}")
    
    data_check_string = "\n".join(data_check_parts)
    
    # Enhanced logging for debugging
    logger.info(f"Building hash from {len(params_dict)} parameters")
    logger.debug(f"Data check string length: {len(data_check_string)}")
    if logger.isEnabledFor(logging.DEBUG):
        # Only log in debug mode to avoid exposing sensitive data
        logger.debug(f"Data check string preview: {data_check_string[:150]}...")
    
    # Log for debugging (be careful not to log sensitive data in production)
    logger.debug(f"Data check string: {data_check_string[:200]}...")  # First 200 chars
    logger.debug(f"Bot token exists: {bool(settings.TELEGRAM_BOT_TOKEN)}")
    logger.debug(f"Bot token length: {len(settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else 0}")
    
    # Calculate secret key: SHA256 of bot token
    # Bot token should be in format: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    # Make sure there's no "Bot " prefix
    bot_token = settings.TELEGRAM_BOT_TOKEN.strip()
    if bot_token.startswith("Bot "):
        bot_token = bot_token[4:].strip()
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_value:
        logger.warning(f"Hash mismatch. Expected: {calculated_hash}, Got: {hash_value}")
        logger.warning(f"Data check string (first 100 chars): {data_check_string[:100]}")
        logger.warning(f"Bot token format check: starts with number? {bot_token[0].isdigit() if bot_token else False}")
        logger.warning(f"Number of parameters: {len(params_dict)}")
        
        # Provide helpful error message
        error_msg = (
            "Invalid hash in init data - authentication failed. "
            "Possible causes:\n"
            "1. Bot token is incorrect or has extra spaces\n"
            "2. init_data was modified or decoded incorrectly\n"
            "3. init_data is expired (more than 24 hours old)\n"
            "4. Make sure to send the RAW query string from Telegram Web App, not decoded values"
        )
        raise ValueError(error_msg)
    
    # Now decode values for actual use
    auth_date_raw = params_dict.get("auth_date")
    if not auth_date_raw:
        raise ValueError("auth_date not found in init data")
    
    try:
        # Try to decode if needed, otherwise use as-is
        auth_date = unquote(auth_date_raw) if '%' in auth_date_raw else auth_date_raw
        auth_timestamp = int(auth_date)
        if time.time() - auth_timestamp > 86400:
            raise ValueError("Auth date is more than 24 hours old")
    except (ValueError, TypeError) as e:
        if "24 hours" in str(e):
            raise
        raise ValueError(f"Invalid auth_date format: {str(e)}")
    
    user_str_raw = params_dict.get("user")
    if not user_str_raw:
        raise ValueError("User not found in init data")
    
    try:
        # Decode the user JSON string if it's URL-encoded
        user_str = unquote(user_str_raw) if '%' in user_str_raw else user_str_raw
        user_data = json.loads(user_str)
        if "id" not in user_data:
            raise ValueError("User ID not found in user data")
        return user_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse user data as JSON: {str(e)}")
    