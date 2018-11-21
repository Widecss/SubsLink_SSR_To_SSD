# -*- coding:utf-8 -*-
# Author:Widecss
# 该脚本依赖于 Flask、Requests 模块
# 请手动安装

import base64
import getopt
import json
import sys

try:
    import requests
except:
    print("载入 Requests 模块失败，脚本已退出。")
    sys.exit(-1)
try:
    from flask import Flask
except:
    print("载入 Flask 模块失败，脚本已退出。")
    sys.exit(-1)


app = Flask(__name__)
# 机场url头，有需要可自行修改
handUrl = "https://www.cordcloud.cc/link/"


def readArgs():
    try:
        args = getopt.getopt(sys.argv[1:], "h")
    except:
        print(False)
        sys.exit(-1)
    return args[1]


def buildServerList(ssrLinkList):
    elementID = 0
    servers = []
    
    for link in ssrLinkList:
        element = {
            "id": elementID, 
            "server": "", 
            "remarks": ""
        }
        elementID += 1

        text = decodeHaveUnderline(link)

        server = text.split(":")[0]
        remarks = text.split("&remarks=")[1].split("&")[0]
        _remarks = decodeUrlBase(remarks)

        # 从备注中获取倍率
        ratio = getRatio(_remarks)
        
        element["server"] = server
        element["remarks"] = _remarks.split("(倍率:")[0]
        element["ratio"] = ratio

        servers += [element]
    
    return servers


def buildSSDJson():
    return {
        "airport": "CordCloud", 
        "port": 1025, 
        "encryption": "aes-128-gcm", 
        "password": "G6l87F", 
        "servers": [{
            "id": 3,
            "server": "www.google.com",
            "remarks": "\u7f8e\u56fd A",
            "ratio": 1
        }]
    }


def decodeBase64(source):
    # 修复长度
    source = fixBase64(source)
    return base64.b64decode(source).decode("utf-8")


def decodeHaveUnderline(text):
    _text = text.replace("_", "/")
    return decodeBase64(_text)


def decodeUrlBase(source):
    _source = fixBase64(source)
    bt = base64.urlsafe_b64decode(_source)
    return bt.decode("utf-8")


def fixBase64(source):
    length = len(source)

    while length % 4 != 0:
        source += "="
        length = len(source)

    return source


# 从备注中获取倍率
# 适配其他机场时请修改或关闭此方法
def getRatio(remark):
    _remark = remark.split("(倍率:")[1]
    _ratio = _remark.split(")")[0]
    return _ratio


def getSubsLink(url):
    try:
        return requests.get(url).text
    except:
        return None


def readFile(path):
    with open(path, 'rb') as fle:
        return fle.read().decode("utf-8")


def writeFile(path, text):
    with open(path, 'wb') as fle:
        fle.write(text.encode("utf-8"))


def getRepoText(subsUrl):
    # 读取base64字符串
    source = getSubsLink(subsUrl)
    if source == None:
        print("获取订阅失败，请检查网络。")
        return "Get Subscription Error"
    # 解码
    _source = source.replace("\n", "")
    ssrLinks = decodeBase64(_source)
    ssrLinks = ssrLinks.replace("\n", "")
    # 分割
    ssrLinkList = ssrLinks.split("ssr://")[1:]

    # 生成ssd链接json
    ssdJson = buildSSDJson()

    # 解码第一个ssr链接
    ssrLink = ssrLinkList[0]
    ssrText = decodeHaveUnderline(ssrLink)
    argList = ssrText.split(":")

    # 过滤协议、混淆
    if ("compatible" not in argList[2]) and (argList[2] != "origin") and \
        ("compatible" not in argList[4]) and (argList[4] != "plain"):

        errorJson = buildSSDJson()
        errorJson["airport"] = "你的订阅不能给ssd用"
        errorJsonStr = json.dumps(errorJson)
        result = base64.b64encode(errorJsonStr.encode("utf-8"))
        return "ssd://" + result.decode("utf-8")

    # 解析端口、加密、密码
    port = argList[1]
    encryption = argList[3]
    password = argList[5].split("/?")[0]
    _password = decodeBase64(password)

    ssdJson["port"] = int(port)
    ssdJson["encryption"] = encryption
    ssdJson["password"] = _password

    # 服务器数组
    servers = buildServerList(ssrLinkList)
    ssdJson["servers"] = servers

    ssdJsonStr = json.dumps(ssdJson)
    ssdLink = base64.b64encode(ssdJsonStr.encode("utf-8"))
    outText = "ssd://" + ssdLink.decode("utf-8")

    return outText


@app.route('/subs/<key>', methods=['GET'])
def get(key=None):
    if key == None:
        print("未输入订阅 Key。")
        return "未输入订阅 Key"

    subsUrl = handUrl + key
    return getRepoText(subsUrl)


if __name__ == "__main__":
    print("\n新订阅链接为： http://localhost:9876/subs/<key>\n")
    app.run(host="localhost", port=9876)
