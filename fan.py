import re
import base64
import requests
import hashlib
import configparser
import json

headers = {'User-Agent': 'okhttp/3.15'}

# 文件路径
config_file_path = 'config.ini'
ok_json_file_path = 'ok.json'
ok_txt_file_path = 'ok.txt'

def get_fan_conf():
    config = configparser.ConfigParser()
    config.read(config_file_path)

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
    url = re.search(r'spider"\:"(.*);md5;', content).group(1)
    content = content.replace(url, './jar/fan.txt')
    content = diy_conf(content)

    with open('go.json', 'w', newline='', encoding='utf-8') as f:
        f.write(content)
    # 本地包
    local_content = local_conf(content)
    with open('go.txt', 'w', newline='', encoding='utf-8') as f:
        f.write(local_content)

    # Update conf.md5
    config.set("md5", "conf", md5)
    with open("config.ini", "w") as f:
        config.write(f)

    jmd5 = re.search(r';md5;(\w+)"', content).group(1)
    current_md5 = config.get("md5", "jar").strip()

    if jmd5 != current_md5:
        # Update jar.md5
        config.set("md5", "jar", jmd5)
        with open("config.ini", "w") as f:
            config.write(f)

        response = requests.get(url)
        with open("./jar/fan.txt", "wb") as f:
            f.write(response.content)

    # 调用更新 MD5 的函数
    update_md5_in_files()

def diy_conf(content):
    #content = content.replace('', './JS/lib/drpy2.min.js')
    #content = content.replace('公众号【神秘的哥哥们】', '豆瓣')
    pattern = r'{"key":"Bili"(.)*\n{"key":"Biliych"(.)*\n'
    replacement = ''
    content = re.sub(pattern, replacement, content)
    pattern = r'{"key":"Nbys"(.|\n)*(?={"key":"cc")'
    replacement = ''
    content = re.sub(pattern, replacement, content)

    return content

def local_conf(content):
    pattern = r'{"key":"88js"(.|\n)*(?={"key":"米搜")'
    replacement = r'{"key":"百度","name":"百度┃采集","type":1,"api":"https://api.apibdzy.com/api.php/provide/vod?ac=list","searchable":1,"filterable":0},\n{"key":"量子","name":"量子┃采集","type":0,"api":"https://cj.lziapi.com/api.php/provide/vod/at/xml/","searchable":1,"changeable":1},\n{"key":"非凡","name":"非凡┃采集","type":0,"api":"http://cj.ffzyapi.com/api.php/provide/vod/at/xml/","searchable":1,"changeable":1},\n{"key":"暴風","name":"暴風┃采集","type":1,"api":"https://bfzyapi.com/api.php/provide/vod/?ac=list","searchable":1,"changeable":1},\n{"key":"索尼","name":"索尼┃采集","type":1,"api":"https://suoniapi.com/api.php/provide/vod","searchable":1,"changeable":1},\n{"key":"快帆","name":"快帆┃采集","type":1,"api":"https://api.kuaifan.tv/api.php/provide/vod","searchable":1,"changeable":1},\n'
    content = re.sub(pattern, replacement, content)
    return content

def update_md5_in_files():
    # 读取 config.ini 文件
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # 获取 config.ini 文件中的 jar MD5 值
    jar_md5 = config.get('md5', 'jar')

    # 更新 ok.json 文件
    with open(ok_json_file_path, 'r', encoding='utf-8') as json_file:
        ok_data = json.load(json_file)

    # 获取 ok.json 文件中的当前 jar MD5 值
    current_jar_md5_json = ok_data['spider'].split(';')[2]

    if jar_md5 != current_jar_md5_json:
        # 更新 ok.json 文件中的 MD5 值
        ok_data['spider'] = ok_data['spider'].replace(current_jar_md5_json, jar_md5)

        # 将更新后的内容写回 ok.json 文件
        with open(ok_json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(ok_data, json_file, ensure_ascii=False, indent=4)
        print("ok.json 中的 MD5 值已更新。")
    else:
        print("ok.json 中的 MD5 值未发生变化。")

    # 更新 ok.txt 文件
    with open(ok_txt_file_path, 'r', encoding='utf-8') as txt_file:
        ok_txt_content = txt_file.read()

    # 获取 ok.txt 文件中的当前 jar MD5 值
    current_jar_md5_txt = ok_txt_content.split(';')[2]

    if jar_md5 != current_jar_md5_txt:
        # 更新 ok.txt 文件中的 MD5 值
        new_txt_content = ok_txt_content.replace(current_jar_md5_txt, jar_md5)

        # 将更新后的内容写回 ok.txt 文件
        with open(ok_txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(new_txt_content)
        print("ok.txt 中的 MD5 值已更新。")
    else:
        print("ok.txt 中的 MD5 值未发生变化。")

if __name__ == '__main__':
    get_fan_conf()
