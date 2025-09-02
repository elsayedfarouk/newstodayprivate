import json
import base64


def json_to_base64(json_obj):
    """
    Convert a JSON object (Python dict or list) to a base64-encoded string.

    Args:
        json_obj (dict or list): The JSON data to encode.

    Returns:
        str: Base64-encoded string of the JSON data.
    """
    try:
        # Convert JSON object to string
        json_str = json.dumps(json_obj)
        # Encode string to bytes
        json_bytes = json_str.encode('utf-8')
        # Base64 encode the bytes
        base64_bytes = base64.b64encode(json_bytes)
        # Convert back to string
        return base64_bytes.decode('utf-8')
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid JSON object: {e}")




json_obj=''

print(json_to_base64(json_obj))