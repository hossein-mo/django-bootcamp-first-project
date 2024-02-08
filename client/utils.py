def create_request(type: str, data: dict, subtype: str = '') -> dict:
    if subtype:
        return {"type": type, 'subtype': subtype, "data": data}
    else:
        return {"type": type, "data": data}
