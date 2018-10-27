def get_json_dict(data, err_code=0, message="Success"):
    ret = {
        'err_code': err_code,
        'message': message,
        'data': data
    }
    return ret

def get_permission_denied_json_dict():
    return get_json_dict(data={}, err_code=-1, message="Perission denied")
