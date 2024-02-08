import hashlib


def hash_password(password: str) -> str:
    """Hash the input string with sha256 algorithm

    Args:
        password (str): input string

    Returns:
        str: hashed input in string format
    """

    password_bytes = password.encode("utf-8")
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    hashed_password = sha256_hash.hexdigest()

    return hashed_password


def create_response(status: bool, type: str, message: str, data: dict | list = {}):
    return {"status": status, "type": type, "message": message, "data": data}
