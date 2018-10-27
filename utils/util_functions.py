from subprocess import call

import hashlib
import requests
from bs4 import BeautifulSoup


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

def get_md5(bytes):
    hash = hashlib.md5()
    hash.update(bytes)
    return hash.hexdigest()


if __name__ == "__main__":
    print(check_fdu_auth("17210240047", "hello"))
