from init_data_py import InitData
from core.config import settings
import requests
import logging

logger = logging.getLogger(__name__)


def validate_init_data(init_data: str):
    parsed_init_data = InitData.parse(init_data)

    if not parsed_init_data.validate(bot_token=settings.TELEGRAM_BOT_TOKEN, lifetime=86400):
        raise ValueError("Invalid init data")

    return parsed_init_data.user


def upload_image_to_telegram(file_bytes: bytes, file_name: str, caption: str) -> str:
    """
    Upload an image to Telegram and return the file URL.
    
    Args:
        file_bytes: The image file as bytes
        file_name: Name of the file
        caption: Caption for the photo
        
    Returns:
        str: URL to the uploaded file
        
    Raises:
        ValueError: If upload fails or response is invalid
        requests.RequestException: If HTTP request fails
    """
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendPhoto"

    files = {'photo': (file_name, file_bytes, 'image/jpeg')}
    data = {'chat_id': settings.TELEGRAM_CHANNEL_ID, 'caption': caption}
    
    response = requests.post(url, files=files, data=data, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    if not result.get('ok'):
        error_description = result.get('description', 'Unknown error')
        logger.error(f"Telegram API error: {error_description}. Full response: {result}")
        raise ValueError(f"Failed to upload image to Telegram: {error_description}")
    
    # Telegram API returns photo array inside 'result' object
    if 'result' not in result:
        logger.error(f"Telegram response missing 'result' field. Full response: {result}")
        raise ValueError(f"Invalid response: result field is missing. Response: {result}")
    
    message_result = result['result']
    
    # Validate photo array exists and has items
    if 'photo' not in message_result:
        logger.error(f"Telegram response missing 'photo' field. Full response: {result}")
        raise ValueError(f"Invalid response: photo array is missing. Response: {result}")
    
    if not isinstance(message_result['photo'], list) or len(message_result['photo']) == 0:
        logger.error(f"Telegram response has empty or invalid photo array. Full response: {result}")
        raise ValueError(f"Invalid response: photo array is empty or invalid. Response: {result}")
    
    # Get the largest photo (last in the array)
    file_id = message_result["photo"][-1]["file_id"]
    
    # Get file info
    file_info_response = requests.get(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getFile",
        params={"file_id": file_id},
        timeout=30
    )
    file_info_response.raise_for_status()
    file_info_result = file_info_response.json()
    
    if not file_info_result.get('ok'):
        raise ValueError(f"Failed to get file info: {file_info_result.get('description', 'Unknown error')}")
    
    if 'result' not in file_info_result or 'file_path' not in file_info_result['result']:
        raise ValueError("Invalid file info response: file_path is missing")
    
    file_path = file_info_result["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
