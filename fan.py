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

    # 新增功能：检查ok.json和ok.txt里的md5值
    update_ok_files(config)
    
def diy_conf(content):
    #content = content.replace('https://fanty.run.goorm.site/ext/js/drpy2.min.js', './JS/lib/drpy2.min.js')
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

def update_ok_files(config):
    # 从config.ini中获取最新的MD5值
    conf_md5 = config.get("md5", "conf").strip()
    
    # 检查ok.json文件
    with open('ok.json', 'r+', encoding='utf-8') as f:
        ok_json = json.load(f)
        if ok_json.get('md5') != conf_md5:
            ok_json['md5'] = conf_md5
            f.seek(0)
            json.dump(ok_json, f, ensure_ascii=False, indent=4)
            f.truncate()
    
    # 检查ok.txt文件
    with open('ok.txt', 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if 'md5' in lines[i]:
                if lines[i].strip().split('=')[1] != conf_md5:
                    lines[i] = f'md5={conf_md5}\n'
                break
        f.seek(0)
        f.writelines(lines)
        f.truncate()
    
if __name__ == '__main__':
    get_fan_conf()
