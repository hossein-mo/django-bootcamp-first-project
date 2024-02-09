def create_request(type: str, subtype: str = '', data: dict = {}) -> dict:
    if subtype:
        return {"type": type, 'subtype': subtype, "data": data}
    else:
        return {"type": type, "data": data}
