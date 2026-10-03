import json

def replace_null_with_default(data, default_value="Not Available"):
    """
    Recursively replaces None (null) values with the given default_value in a dictionary or list.

    Args:
        data (dict | list): The input JSON-like dictionary or list.
        default_value (str): The replacement value for None.

    Returns:
        dict | list: The processed dictionary or list with None values replaced.
    """
    if isinstance(data, dict):
        return {k: replace_null_with_default(v, default_value) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_null_with_default(item, default_value) for item in data]
    elif data is None:
        return default_value
    return data