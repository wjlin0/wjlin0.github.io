import os
import re

chrome_path = f"{os.path.expanduser('~')}/Library/Application Support/Google/Chrome"
chrome_state_path = os.path.join(chrome_path, "Local State")
data = open(chrome_state_path).read()
# regex = "\"encrypted_key\":\"(.*?)\""

encrypted_key = re.findall(r"\"encrypted_key\":\"(.*?)\"", data)
print(encrypted_key)
