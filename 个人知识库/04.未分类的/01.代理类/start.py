#!/usr/bin/env python3
import _thread
import base64
import datetime
import json
import os
import re
import socket
import uuid
from urllib.parse import quote
import yaml

myDomain = ""  # 自己的域名，即vps上解析的域名

# 再运行前配置后github相关参数（需要有一个创建好的github项目和github的token）
gitName = ""  # github项目名称
gitUser = ""  # github的用户名
gitAccessKey = ""  # github的key
# 端口数量 保证不能重复

Port = [
    1111,
    1112,
    1113,
    1114,
    1115,
    1116,
    1117,
    1118,
    1119,
    1120,
]
note = quote("自己的vps，不要乱来，谢谢")  # 每个节点的备注
vpnCount = 10  # 就是开的节点数量 看vps的性能 一般可以开到10个 低就 2-3个
# 下面不懂可以不动

gitAuthPath = f"https://{gitUser}:{gitAccessKey}@github.com/{gitUser}/{gitName}.git"
xrayJsonPath = "./conf"  # conf 存放位置,不懂python不要动
githubPath = "./github.com/subscribe"  # 不懂python不要动
lock = _thread.allocate_lock()  # 不懂python不要动

t = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d:%H")  # 不懂python不要动


def updateDockerYaml(defaultPort, count):
    config = {
    }
    for i in range(1, count + 1):
        xrayName = "xray" + str(i)
        port = defaultPort[i-1]
        tmp = {
            "image": "wjlin0/xray:v1",
            "hostname": xrayName,
            "container_name": xrayName,
            "ports": [f"{port}:443"],
            "volumes": [f"{xrayJsonPath}:/conf"],
            "command": ["/bin/bash", "/conf/start.sh"]
        }
        config[xrayName] = tmp
    docker_compose_yaml_dict = {"version": str("3.0"),
                                "services": config
                                }
    with open("docker-compose.yml", "w", encoding="utf-8") as f:
        yaml.dump(docker_compose_yaml_dict, f)
    return yaml.dump(docker_compose_yaml_dict)


def updateXrayJson(uuid: str):
    xrayJson = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 443,
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": uuid,
                            "flow": "xtls-rprx-direct"
                        }
                    ],
                    "decryption": "none",
                    "fallbacks": [
                        {
                            "dest": 60000,
                            "alpn": "",
                            "xver": 1
                        },
                        {
                            "dest": 60001,
                            "alpn": "h2",
                            "xver": 1
                        }
                    ]
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "xtls",
                    "xtlsSettings": {
                        "minVersion": "1.2",
                        "certificates": [
                            {
                                "certificateFile": f"/conf/ssl/{myDomain}.crt",
                                "keyFile": f"/conf/ssl/{myDomain}.key"
                            }
                        ]
                    }
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": [
                        "http",
                        "tls"
                    ]
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "freedom"
            }
        ]
    }
    if not os.path.exists(xrayJsonPath):
        os.makedirs(xrayJsonPath)
    with open(os.path.join(xrayJsonPath, "config.json"), "w", encoding="utf-8") as f:
        json.dump(xrayJson, f, sort_keys=True, indent=4, )


def update(count, uuid4, domain, defaultPort, Output):
    os.system(f"cd {Output} && git pull origin main")
    url = f"STATUS=更新时间:{t}\nREMARKS=wjlin0.com\n"
    output = os.path.join(Output, "url")
    for i in range(1, count + 1):
        port = defaultPort[i-1]
        url += f"vless://{uuid4}@{domain}:{port}?flow=xtls-rprx-direct&host=&security=xtls&sni=#{note}\n"
    if not os.path.exists(output):
        open(output, "w").close()
    old = open(output).read()
    oldDecode = base64.b64decode(old).decode("utf-8")
    for o in oldDecode.split("\n"):
        u = "".join(re.findall(".*://.*@.*:\d*?.*", o))
        if u == "":
            continue
        if domain not in u:
            url += u + "\n"
    with open(output, "w") as f:
        f.write(base64.b64encode(bytes(url, encoding="utf-8")).decode("utf-8").strip())
    return url


def IsOpen(port, ip="127.0.0.1"):
    try:
        if port >= 65535:
            print(u'端口扫描结束')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((ip, port))
        if result == 0:
            lock.acquire()
            print(ip, u':', port, u'端口已占用')
            lock.release()
            return False
        else:
            return True
    except:
        print(u'端口扫描异常')


def updateGithub(Output):
    os.environ["GITHUB_TOKEN"] = gitAccessKey
    dirFile = os.path.abspath(Output)  # code的文件位置，我默认将其存放在根目录下
    os.system(f"cd {dirFile} && git pull origin main && git add url && git commit -m \"update {t}\" && git push origin main")
    print("Successful push!")


def updateDocker():
    os.system("docker-compose up -d")


def init():
    try:
        if os.getuid() != 0:
            print("为了保证文件权限问题，请用root用户运行...")
            return False
        myDomainKey = os.path.abspath(os.path.join(xrayJsonPath, "ssl", myDomain + ".key"))
        myDomainCrt = os.path.abspath(os.path.join(xrayJsonPath, "ssl", myDomain + ".crt"))
        if not os.path.exists(xrayJsonPath):
            os.makedirs(xrayJsonPath)
            print(f"证书 {myDomainKey}、{myDomainCrt} 缺失\n请将证书导入至 .{os.path.join(xrayJsonPath, 'ssl')} 中")
            return False
        if not os.path.exists(githubPath):
            os.makedirs(githubPath)
            cmd = f"cd {githubPath} && git init && git checkout -b main && git remote add origin {gitAuthPath} && git pull origin main"
            print(cmd)
            os.system(cmd)

        if os.path.exists(myDomainKey) == False or os.path.exists(myDomainCrt) == False:
            print(f"证书 {myDomainKey}、{myDomainCrt} 缺失\n请将证书导入至 ./conf/ssl/ 中")
            return False

        cmd_exists = lambda x: any(
            os.access(os.path.join(path, x), os.X_OK) for path in os.environ["PATH"].split(os.pathsep)
        )
        if not cmd_exists("docker"):
            print("docker不存在 -> 正在安装docker")
            try:
                os.system("curl -sSL https://get.daocloud.io/docker | sh")
            except Exception as e:
                print(f"安装docker失败,请手动安装 -> {e}")
                return False
        if not cmd_exists("docker-compose"):
            print("docker不存在 -> 正在安装docker")
            try:
                os.system(
                    "sudo curl -L https://get.daocloud.io/docker/compose/releases/download/v2.4.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose")
                os.system("chmod +x /usr/local/bin/docker-compose")
                os.system("sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose")
            except Exception as e:
                print(f"安装docker-compose失败,请手动安装 -> {e}")
                return False
        os.system("docker-compose down")
        if len(Port) < vpnCount:
            print("端口数 不能小于 节点数 即-> len（Port）>= vpnCount ")
            return False
        for p in Port:
            if not IsOpen(p):
                return False
        os.system("service docker restart")
        return True

    except Exception as e:
        print(e)
        return False


def updateNginx(domain):
    conf = """
server
{
        listen 80;
        listen [::]:80;
        server_name %s;
        return 301 https://$http_host$request_uri;

        access_log  /dev/null;
        error_log  /dev/null;
}

server
{
        listen 127.0.0.1:60000 proxy_protocol;
        listen 127.0.0.1:60001 http2 proxy_protocol;
        server_name %s;
        index index.html index.htm index.php default.php default.htm default.html;
        root /var/www/html;
        add_header Strict-Transport-Security "max-age=63072000" always;

        location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$
        {
                expires   30d;
                error_log off;
        }

        location ~ .*\.(js|css)?$
        {
                expires   12h;
                error_log off;
        }
}
    """ % (domain, domain)
    with open(os.path.join(xrayJsonPath, "web.conf"), "w", encoding="utf-8") as f:
        f.write(conf)

    return conf


def updateBash():
    bash = """
#!/bin/bash
cp /conf/web.conf /etc/nginx/conf.d/ && \
        service nginx restart && \
        cp /var/www/html/index.nginx-debian.html /var/www/html/index.html && \
        /data/xray/xray run -config /conf/config.json
"""
    with open(os.path.join(xrayJsonPath, "start.sh"), "w") as f:
        f.write(bash)
    return bash


def validate():
    ok = True
    if myDomain == "":
        ok = False
        print("myDomain 为空，请配置")
    if gitName == "":
        ok = False
        print("gitName 为空，请配置")
    if githubPath == "":
        ok = False
        print("githubPath 为空，请配置")
    if gitAccessKey == "":
        ok = False
        print("gitAccessKey 为空，请配置")
    if gitUser == "":
        ok = False
        print("gitUser 为空，请配置")
    return ok


if __name__ == '__main__':
    if not validate():
        exit(0)
    if not init():
        exit(0)
    webconf = updateNginx(myDomain)
    print(webconf)
    bash = updateBash()
    print(bash)
    config = updateDockerYaml(Port, vpnCount)
    print(config)
    uuid4 = str(uuid.uuid4())
    updateXrayJson(uuid4)
    url = update(vpnCount, uuid4, myDomain, Port, githubPath)
    print(url)
    updateDocker()
    updateGithub(githubPath)
    print(f"更新完成，订阅链接 -> https://raw.githubusercontent.com/{gitUser}/{gitName}/main/url")