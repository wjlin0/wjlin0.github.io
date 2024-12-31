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
import csv
import re

# 全局定义浏览器名称和对应的钥匙串条目（第一个为 key 名，第二个为浏览器目录名称）
keychain_names = {
    'chrome': ['Chrome', 'Google/Chrome'],
    'edge': ['Microsoft Edge', 'Microsoft Edge'],
    'chromium': ['Chromium', 'Chromium'],
    'quark': ['Quark Key', 'Quark'],
    'qq': ['QQBrowser', 'QQBrowser'],
    '360chrome': ['', '360Chrome'],
    'chrome beta': ['Chrome', 'Google/Chrome Beta'],
    'Brave': ['Brave', 'BraveSoftware/Brave-Browser'],
    'opera': ['Opera', 'com.operasoftware.Opera'],
    'operagx': ['Opera', 'com.operasoftware.OperaGX'],
    'vivaldi': ['Vivaldi', 'Vivaldi'],
    'coccoc': ['CocCoc', 'CocCoc'],
    'yandex': ['Yandex', 'Yandex'],
    'arc': ['Arc', 'Arc/User Data'],

}
keychain_names_firefox = {
    # firefox

    'firefox': ['Firefox', 'Firefox']
}


class FirefoxPasswordDecryptor:
    def __init__(self, browser_name):
        self.browser_name = browser_name
        self.loginData, self.safeStorageKey = self.get_browser_data_and_key()  # 获取登录数据和 Safe Storage Key
        self.decrypted_data = []  # 存储解密后的数据
        self.password_strength_count = {"弱": 0, "中": 0, "强": 0}  # 统计各个密码强度的数量
        self.login_count = 0  # 用于存储查询到的登录记录总数
        self.output_filename = f"out-{self.browser_name}.csv"  # 设置输出文件名，自动根据浏览器命名
        self.total_files_processed = 0  # 统计处理的文件数
        self.file_login_count = {}  # 用于存储每个文件的登录记录数量
        if not self.safeStorageKey:
            print(f"\t❌ Warning: 未能获取 {self.browser_name} 的 Safe Storage Key，密码将不会进行强度检查")
        else:
            print(f"\t🎉 成功获取 {self.browser_name} 的 Safe Storage Key")

    def get_browser_data(self):
        tmp_data = []
        base_dirs = [f"/Users/{user}/Library/Application Support" for user in os.listdir("/Users") if
                     os.path.isdir(f"/Users/{user}")]
        global_base_dirs = ["/Library/Application Support"]
        login_data = []
        for base_dir in base_dirs + global_base_dirs:
            browser_dir = self.get_browser_directory()
            pattern = os.path.join(base_dir, browser_dir, '**', 'key4.db')
            login_paths = glob.glob(pattern, recursive=True)
            tmp_data.extend(login_paths)
        for l_d in tmp_data:
            # 得到 l_d 此时的路径
            path = os.path.dirname(l_d)
            logins_json = os.path.join(path, 'logins.json')
            if os.path.exists(logins_json):
                login_data.append([l_d, logins_json])
        return login_data

    def get_keychain_name(self):
        """
            根据浏览器名称返回对应的钥匙串条目名称
        """
        if self.browser_name in keychain_names_firefox:
            return keychain_names_firefox[self.browser_name][0]
        else:
            raise Exception(f"\tUnsupported browser for keychain: {self.browser_name}")

    def get_browser_data_and_key(self):
        """
        根据浏览器名称判断并获取对应的 Login Data 路径和
        """
        login_data = self.get_browser_data()

        if not login_data:
            raise Exception(f"\tLogin Data not found for {self.browser_name}")

        print(f"\t💫 {self.browser_name.capitalize()} 找到 {len(login_data)} 个文件：")
        for file in login_data:
            print(f"\t   {file[0]}")

        login_data_raw = []
        for t in login_data:
            pass
    def get_master_key(self, sql_file):
        """
        获取 Master Key
        """
        fd = os.open(sql_file, os.O_RDONLY)  # 以只读模式打开数据库
        database = sqlite3.connect(f'/dev/fd/{fd}')
        os.close(fd)
        sql_get_meta_data = "SELECT item1, item2 FROM metadata WHERE id = 'password'"
        sql_get_nss_private = "SELECT a11, a102 FROM nssPrivate"
        with database:
            item1, item2 = database.execute(sql_get_meta_data).fetchone()
            a11, a102 = database.execute(sql_get_nss_private).fetchone()
            finallyKey = self.decrypt_master_key(item1, item2, a11, a102)

    def decrypt_master_key(self, item1, item2, a11, a102):
        print(item1, item2, a11, a102)

        pass






    def get_browser_directory(self):
        """
        根据浏览器名称返回对应的浏览器目录名称
        """
        if self.browser_name in keychain_names_firefox:
            return keychain_names_firefox[self.browser_name][1]
        else:
            raise Exception(f"\tUnsupported browser for directory: {self.browser_name}")


class ChromiumPasswordDecryptor:
    def __init__(self, browser_name):
        self.browser_name = browser_name  # 浏览器名称 (如 'chrome', 'edge', 'chromium')
        self.loginData, self.safeStorageKey = self.get_browser_data_and_key()  # 获取登录数据和 Safe Storage Key
        self.decrypted_data = []  # 存储解密后的数据
        self.password_strength_count = {"弱": 0, "中": 0, "强": 0}  # 统计各个密码强度的数量
        self.login_count = 0  # 用于存储查询到的登录记录总数
        self.output_filename = f"out-{self.browser_name}.csv"  # 设置输出文件名，自动根据浏览器命名
        self.total_files_processed = 0  # 统计处理的文件数
        self.file_login_count = {}  # 用于存储每个文件的登录记录数量
        if not self.safeStorageKey:
            print(f"\t❌ Warning: 未能获取 {self.browser_name} 的 Safe Storage Key，密码将不会进行强度检查")
        else:
            print(f"\t🎉 成功获取 {self.browser_name} 的 Safe Storage Key")

    def get_keychain_name(self):
        """
        根据浏览器名称返回对应的钥匙串条目名称
        """
        if self.browser_name in keychain_names:
            return keychain_names[self.browser_name][0]
        else:
            raise Exception(f"\tUnsupported browser for keychain: {self.browser_name}")

    def get_browser_directory(self):
        """
        根据浏览器名称返回对应的浏览器目录名称
        """
        if self.browser_name in keychain_names:
            return keychain_names[self.browser_name][1]
        else:
            raise Exception(f"\tUnsupported browser for directory: {self.browser_name}")

    def get_all_user_login_paths(self):
        """
        查找系统中所有用户的 Login Data 文件路径。
        这将扫描 /Users 目录下的每个用户文件夹，并查找对应的浏览器的 Login Data 文件。
        同时检查全局安装目录 /Library/Application Support。
        """
        login_data = []
        base_dirs = [f"/Users/{user}/Library/Application Support" for user in os.listdir("/Users") if
                     os.path.isdir(f"/Users/{user}")]
        global_base_dirs = ["/Library/Application Support"]

        # 查找用户目录和全局目录
        for base_dir in base_dirs + global_base_dirs:
            browser_dir = self.get_browser_directory()  # 获取浏览器的目录名称
            pattern = os.path.join(base_dir, browser_dir, '**', 'Login Data')
            login_paths = glob.glob(pattern, recursive=True)
            login_data.extend(login_paths)

        return login_data

    def get_browser_data_and_key(self):
        """
        根据浏览器名称判断并获取对应的 Login Data 路径和 Safe Storage Key
        """
        login_data = self.get_all_user_login_paths()

        if not login_data:
            raise Exception(f"\tLogin Data not found for {self.browser_name}")

        print(f"\t💫 {self.browser_name.capitalize()} 找到 {len(login_data)} 个文件：")
        for file in login_data:
            print(f"\t   {file}")

        # 获取 Safe Storage Key
        keychain_name = self.get_keychain_name()  # 获取钥匙串条目名称
        if keychain_name == "":
            return login_data, None
        try:
            safe_storage_key = subprocess.run(
                f"security 2>&1 > /dev/null find-generic-password -ga '{keychain_name}' | awk '{{print $2}}'",
                shell=True, text=True, capture_output=True).stdout.strip().replace("\"", "")
            # 判断是否以 SecKeychainSearchCopyNext 开头
            if safe_storage_key.startswith('SecKeychainSearchCopyNext'):
                return login_data, None

            return login_data, safe_storage_key
        except subprocess.CalledProcessError:
            return login_data, None

    def decrypt_password(self, encrypted_value, iv, key=None):
        """
        解密密码
        """
        hexKey = binascii.hexlify(key).decode()  # 将字节转换为十六进制字符串
        hexEncPassword = base64.b64encode(encrypted_value[3:]).decode()  # 将字节转换为 Base64 编码字符串
        try:
            decrypted = subprocess.run(
                f"openssl enc -base64 -d -aes-128-cbc -iv '{iv}' -K {hexKey} <<< {hexEncPassword} 2>/dev/null",
                shell=True, text=True, capture_output=True).stdout
        except Exception as e:
            decrypted = "ERROR retrieving password"
        return decrypted

    def process_login_data(self, loginData):
        """
        处理并解密登录数据
        """
        iv = ''.join(('20',) * 16)  # 初始化向量 (IV)，根据 Chromium 源码
        key = hashlib.pbkdf2_hmac('sha1', self.safeStorageKey.encode(), b'saltysalt', 1003)[
              :16] if self.safeStorageKey else None
        shutil.copy(loginData, '/tmp/1.db')  # 将登录数据库文件复制到 /tmp 目录

        fd = os.open("/tmp/1.db", os.O_RDONLY)  # 以只读模式打开数据库
        database = sqlite3.connect(f'/dev/fd/{fd}')
        os.close(fd)

        sql_count = 'select count(*) from logins'
        count = database.execute(sql_count).fetchone()[0]
        self.login_count += count  # 保存查询到的总数
        self.file_login_count[loginData] = count  # 记录该文件的登录记录数量

        sql = 'select username_value, password_value, origin_url from logins'

        with database:
            for user, encryptedPass, url in database.execute(sql):
                if user == "" or encryptedPass[:3] != b'v10':  # 如果没有存储密码或密码没有加密
                    continue
                else:
                    urlUserPassDecrypted = (
                        url,
                        user,
                        self.decrypt_password(encryptedPass, iv, key=key),
                        loginData  # 将文件名一起存储
                    ) if self.safeStorageKey else (url, user, encryptedPass, loginData)
                    self.decrypted_data.append(urlUserPassDecrypted)

    def process_all_logins(self):
        """
        处理所有登录数据并解密
        """
        for profile in self.loginData:
            self.process_login_data(profile)
            self.total_files_processed += 1  # 增加文件处理计数

    @staticmethod
    def check_password_strength(password):
        """
        判断密码强度：弱、中、强
        密码规则：长度 >= 8，必须包含字母、数字、特殊字符
        """
        if len(password) < 8:
            return "弱"

        # 判断是否包含数字、字母和特殊字符
        has_digit = re.search(r'\d', password)  # 是否包含数字
        has_letter = re.search(r'[A-Za-z]', password)  # 是否包含字母
        has_special = re.search(r'[\W_]', password)  # 是否包含特殊字符

        if has_digit and has_letter and has_special:
            return "强"
        elif has_digit or has_letter:
            return "中"
        else:
            return "弱"

    def save_to_file(self):
        """
        保存数据到文件
        """
        with open(f"{self.output_filename}", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # 使用中文标题
            writer.writerow(["索引", "网址", "用户名", "密码", "密码强度", "来源文件"])  # 添加索引和来源文件列
            for idx, data in enumerate(self.decrypted_data, 1):  # 添加索引列，起始为 1
                password_strength = self.check_password_strength(data[2]) if self.safeStorageKey else "未检查"
                writer.writerow([idx, data[0], data[1], data[2], password_strength, data[3]])  # 写入每一行数据

    def print_password_summary(self):
        """
        打印密码强度的统计信息
        """
        if self.safeStorageKey and len(self.decrypted_data) > 0:

            weak_count = sum(1 for data in self.decrypted_data if
                             self.check_password_strength(data[2]) == "弱") if self.safeStorageKey else 0
            medium_count = sum(1 for data in self.decrypted_data if
                               self.check_password_strength(data[2]) == "中") if self.safeStorageKey else 0
            strong_count = sum(1 for data in self.decrypted_data if
                               self.check_password_strength(data[2]) == "强") if self.safeStorageKey else 0

            print(f"\t🎉 {self.browser_name.capitalize()}浏览器 总共查询到 {self.login_count} 条登录记录：")
            print(f"\t   高强度密码：{strong_count} 个")
            print(f"\t   中强度密码：{medium_count} 个")
            print(f"\t   低强度密码：{weak_count} 个")
            print(f"\t   数据已保存到 {self.output_filename}")  # 输出数据保存位置

            # 打印每个文件的登录记录数量
            print("\t💫 每个文件的登录记录数量：")
            for file, count in self.file_login_count.items():
                print(f"\t   {file}: {count} 条")
        elif not self.safeStorageKey and len(self.decrypted_data) > 0:
            print(f"\t🎉 {self.browser_name.capitalize()}浏览器 总共查询到 {self.login_count} 条登录记录：")
            print(f"\t   数据已保存到 {self.output_filename}")
            # 打印每个文件的登录记录数量
            print("\t💫 每个文件的登录记录数量：")
            for file, count in self.file_login_count.items():
                print(f"\t   {file}: {count} 条")
        else:
            print(f"\t❌ 未查询到 {self.browser_name} 的登录记录。")


def get_supported_browsers():
    """
    获取系统中已安装并支持的浏览器名称。
    根据浏览器的安装目录判断哪些浏览器已安装。
    """
    supported_browsers = []

    # 检查每个浏览器是否存在于系统中
    for browser in keychain_names.keys():
        # 构建浏览器的目录路径
        user_dirs = [f"/Users/{user}/Library/Application Support" for user in os.listdir("/Users") if
                     os.path.isdir(f"/Users/{user}")]
        global_dirs = ["/Library/Application Support"]

        # 查找用户目录和全局目录中是否存在浏览器目录
        browser_found = False
        for base_dir in user_dirs + global_dirs:
            browser_dir = keychain_names[browser][1]  # 获取对应的浏览器目录
            if os.path.exists(f"{base_dir}/{browser_dir}"):
                browser_found = True
                break

        if browser_found:
            supported_browsers.append(browser)

    return supported_browsers

def main():
    fire = FirefoxPasswordDecryptor('firefox')
    fire.get_master_key('/Users/wjl/Library/Application Support/Firefox/Profiles/o3qkajg4.default-release-1715065004489/key4.db')

#
# def main():
#     try:
#         supported_browsers = get_supported_browsers()
#         print(
#             f"🎉 找到 {len(supported_browsers)} 个支持的浏览器：{', '.join([b.capitalize() for b in supported_browsers])}")
#
#         if not supported_browsers:
#             print("❌ 系统中没有检测到支持的浏览器。")
#             sys.exit(1)
#
#         for browser_name in supported_browsers:
#             print(f"💫 处理 {browser_name.capitalize()} 浏览器：")
#             # 创建对应的密码解密对象
#             decryptor = ChromiumPasswordDecryptor(browser_name)
#
#             # 处理所有登录数据并解密
#             decryptor.process_all_logins()
#
#             # 保存数据到文件
#             if decryptor.decrypted_data:
#                 decryptor.save_to_file()
#
#             # 打印密码强度的统计信息
#             decryptor.print_password_summary()
#
#     except Exception as e:
#         print(f"\tError: {e}")
#         sys.exit(1)


if __name__ == "__main__":
    main()
