def get_user_private_dict(account):

    user_dict = get_user_public_dict(account)

    user_dict['mobile_phone'] = account.mobile_phone
    user_dict['wechat'] = account.wechat
    user_dict['qq'] = account.qq

    return user_dict

def get_user_public_dict(account):
    user_dict = {
        'username': account.user.username,
        'id': account.user.id,
        'nickname': account.nickname,
        'gender': account.gender,
        'icon': account.icon.url,
        'school': account.school,
        'major': account.major,
    }
    return user_dict