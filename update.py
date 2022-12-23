#!/usr/bin/env bash
import hashlib
import json
import re

import time
import datetime

import os
import time


def readConfig():
    with open('name.json', 'r', encoding="utf-8") as f:
        return json.load(f)


def writeConfig(file):
    with open('name.json', 'w', encoding="utf-8") as f:
        f.write(json.dumps(file, indent=4, sort_keys=True))


def Init():
    updatefile = {"新增": {}, "补充": {}, "删除": {}}
    file = getFileHash()
    writeConfig(file)
    for k, v in file['files'].items():
        updatefile["新增"][k] = get_FileModifyTime(k)
    print(updatefile)
    if updatefile != {"新增": {}, "补充": {}, "删除": {}}:
        update(updatefile)
    exit()


def getFileHash():
    file = {"gengxing": 1, "files": {}}
    for filepath, dirnames, filenames in os.walk("./docs/个人知识库/"):
        for filename in filenames:
            if ".md" in filename:
                f = os.path.abspath(filepath + "\\" + filename)
                md5hash = hashlib.md5(open(f, encoding="utf-8").read().encode("utf-8"))
                md5 = md5hash.hexdigest()
                file["files"][f] = md5
                # print(f + "=" + md5)
    return file


'''把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12'''


def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


'''获取文件的大小,结果保留两位小数，单位为MB'''


def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


'''获取文件的访问时间'''


def get_FileAccessTime(filePath):
    t = os.path.getatime(filePath)
    return TimeStampToTime(t)


'''获取文件的创建时间'''


def get_FileCreateTime(filePath):
    t = os.path.getctime(filePath)
    return TimeStampToTime(t)


'''获取文件的修改时间'''


def get_FileModifyTime(filePath):
    t = os.path.getmtime(filePath)
    return TimeStampToTime(t)


def update(updatefile: dict):
    f = open("更新日志.md", 'r', encoding="utf-8")
    content = f.read()
    f.close()
    result = "|:---|:---|:---|\n"
    result = "|时间|路径|操作|\n" + result
    time_S = time.localtime(time.time())
    title = f"## {str(time_S.tm_year).zfill(4)}年{str(time_S.tm_mon).zfill(2)}月{str(time_S.tm_mday).zfill(2)}日"
    if updatefile == {"新增": {}, "补充": {}, "删除": {}}:
        exit()
    if updatefile["新增"] != {}:
        for k, v in updatefile["新增"].items():
            tmp = re.findall('^.*?个人知识库\\\\(.*?)\.md$', k)[0]
            tmp = str(tmp).replace("\\", "/")
            result += f"| {v} | [{tmp}](个人知识库/{tmp}.html) | 新增 |\n"
    if updatefile["补充"] != {}:
        for k, v in updatefile["补充"].items():
            tmp = re.findall('^.*?个人知识库\\\\(.*?)\.md$', k)[0]
            tmp = str(tmp).replace("\\", "/")
            result += f"| {v} | [{tmp}](个人知识库/{tmp}.html) | 补充更新 |\n"
    if updatefile["删除"] != {}:
        for k, v in updatefile["删除"].items():
            tmp = re.findall('^.*?个人知识库\\\\(.*?)\.md$', k)[0]
            tmp = str(tmp).replace("\\", "/")
            result += f"| {v} | [{tmp}](个人知识库/{tmp}.html) | 删除 |\n"
    # 组合
    content += title
    content += "\n\n"
    content += result
    f = open("更新日志.md", 'w', encoding="utf-8")
    f.write(content)
    f.close()


if __name__ == '__main__':
    old_file = dict(readConfig())
    if old_file['gengxing'] == 0:
        Init()
    new_file = getFileHash()
    updatefile = {"新增": {}, "补充": {}, "删除": {}}
    for k, v in old_file['files'].items():
        if k not in new_file['files'].keys():
            updatefile["删除"][k] = TimeStampToTime(time.time())
    for k, v in new_file['files'].items():
        if k not in old_file['files'].keys():
            updatefile["新增"][k] = get_FileModifyTime(k)
            old_file['files'][k] = v
        if new_file['files'][k] != old_file['files'][k]:
            updatefile["补充"][k] = get_FileModifyTime(k)
    writeConfig(new_file)
    print(updatefile)
    if updatefile != {"新增": {}, "补充": {}, "删除": {}}:
        update(updatefile)
