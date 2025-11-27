import hmac
import hashlib
import time
import json
from core.config import settings

def validate_init_data(init_data: str) -> dict:
    """Validate Telegram init data and return the user data"""

    from urllib.parse import parse_qs
    params = parse_qs(init_data)

    if "hash" not in params:
        raise ValueError("hash not found in init data")
    
    hash_value = params.pop("hash")[0]
    data_check_string = "\n".join([f"{k}={v[0]}" for k, v in sorted(params.items())])

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_value:
        raise ValueError("Invalid hash in init data")
    
    auth_date = params.get("auth_date", [0])[0]
    if time.time() - int(auth_date) > 86400:
        raise ValueError("Auth date is more than 24 hours old")
    
    user_str = params.get("user", [None])[0]
    if not user_str:
        raise ValueError("User not found in init data")
    
    user_data = json.loads(user_str)
    return user_data
    