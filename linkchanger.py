# -*- coding:utf-8 -*-
# Author:Widecss
# 为减少代码量该脚本使用了 Requests 模块
# 请手动安装

import base64
import getopt
import json
import sys

try:
    import requests
except:
    print("缺少 Requests 模块，程序已退出。")
    sys.exit(-1)


def readArgs():
    try:
        args = getopt.getopt(sys.argv[1:], "h")
        # opts = [('-a', "abc"), ('-b', 'cde')]
        # args = ['123']
    except:
        print(False)
        # print('解析参数失败！程序已退出。')
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
        ratio = getRatio(_remarks)
        
        element["server"] = server
        element["remarks"] = _remarks.split("(倍率:")[0]
        element["ratio"] = ratio

        servers += [element]
    
    return servers


def buildSSDJson():
    return {
        "airport": "CordCloud", 
        "port": 0, 
        "encryption": "", 
        "password": "", 
        "servers": {}
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


def getRatio(remark):
    _remark = remark.split("(倍率:")[1]
    _ratio = _remark.split(")")[0]
    return _ratio


def getSubsLink(url):
    return requests.get(url).text


def readFile(path):
    with open(path, 'rb') as fle:
        return fle.read().decode("utf-8")


def writeFile(path, text):
    with open(path, 'wb') as fle:
        fle.write(text.encode("utf-8"))


if __name__ == "__main__":
    # 读取参数
    argLink = readArgs()[0]
    if argLink.strip == "":
        print("请输入订阅链接[http(s)://*]。脚本已退出.")
        sys.exit(-1)
    # 读取base64字符串
    source = getSubsLink(argLink)
    # 解码
    _source = source.replace("\n", "")
    ssrLinks = decodeBase64(_source)
    ssrLinks = ssrLinks.replace("\n", "")
    # 分割
    ssrLinkList = ssrLinks.split("ssr://")[1:]

    # 生成ssd链接json
    ssdJson = buildSSDJson()

    # 端口、加密、密码
    ssrLink = ssrLinkList[0]
    ssrText = decodeHaveUnderline(ssrLink)
    argList = ssrText.split(":")

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
    writeFile("Output.txt", outText)

    print("获取成功！已输出文件Output.txt")