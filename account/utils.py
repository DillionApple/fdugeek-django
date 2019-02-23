import random
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

from django.conf import settings

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

def generate_account_confirm_code():

    ret = ''

    for i in range(64):
        ret = ret + str(random.randint(0, 10))

    return ret

def send_confirm_code_to_fdu_mailbox(username, confirm_code):

    message = """
你好：
    请点击下面的链接来验证您的在FDU GEEK注册时使用的邮箱，链接30分钟内有效：
    {host}/account/confirm_register/?username={username}&confirm_code={confirm_code}
    """.format(host=settings.DEPLOY_HOST, username=username, confirm_code=confirm_code)
    subject = "FDU GEEK邮箱验证（no reply）"
    from_addr = "fdugeek_admin@163.com"
    to_addr = "{0}@fudan.edu.cn".format(username)
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_password = settings.SMTP_PASSWORD

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    s = smtplib.SMTP_SSL(host=smtp_host, port=smtp_port)
    s.login(from_addr, smtp_password)
    s.send_message(msg)
    s.quit()

def check_fdu_auth(username, password):

    form_data = {
        'local': 'zh_CN',
        'uid': username,
        'password': password,
        'domain': 'fudan.edu.cn',
        'nodetect': 'false',
        'action:login': ''
    }


    session = requests.session()
    response = session.post('http://mail.fudan.edu.cn/coremail/index.jsp', data=form_data)

    soup = BeautifulSoup(response.text, features="html.parser")

    try:
        user_email_name = soup.select('.account')[0].text
    except:
        return None

    return user_email_name

