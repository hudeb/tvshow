import re
import base64
import requests
import hashlib
import configparser

headers = {'User-Agent': 'okhttp/3.15'}

def get_fan_conf():
    config = configparser.ConfigParser()
    config.read("config.ini")

    url = 'http://饭太硬.com/tv'
    response = requests.get(url, headers=headers)
    match = re.search(r'[A-Za-z0]{8}\*\*(.*)', response.text)

    if not match:
        return
    result = match.group(1)

    m = hashlib.md5()
    m.update(result.encode('utf-8'))
    md5 = m.hexdigest()

    try:
        old_md5 = config.get("md5", "conf")
        if md5 == old_md5:
            print("No update needed")
            return
    except:
        pass

    content = base64.b64decode(result).decode('utf-8')

    # Update conf.md5
    config.set("md5", "conf", md5)
    with open("config.ini", "w") as f:
        config.write(f)

if __name__ == '__main__':
    get_fan_conf()
