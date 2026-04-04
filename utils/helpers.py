import base64
from typing import Tuple
from .errors import InvalidBase64Error

def decode_base64_file(base64_string: str) -> bytes:
    try:
        # Sometimes base64 strings have data URI prefix like 'data:image/jpeg;base64,'
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
            
        file_bytes = base64.b64decode(base64_string, validate=True)
        return file_bytes
    except Exception as e:
        raise InvalidBase64Error(f"Failed to decode base64 string: {str(e)}")
