# Challenge: dreamhack - testsite

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/75/
flask로 작성된 image viewer라고 한다. 플래그는 /app/flag.txt에 있다


## 문제 풀이
step 1 - admin 권한 얻기
* app.py의 코드를 뜯어보자. /logintest에서 로그인에 실패하면 해당 유저의 이름으로 어떠한 로직을 거쳐 오류코드를 보여준다. /login의 코드를 보면 여기서 반환된 값을 document.cookie = "id={setcookie(username)}";로 사용한다. 따라서 guest 계정으로 로그인한 후, 쿠키에 admin으로 logintest에서 login에 실패한 다음 반환된 값을 넣어 /admin에 접속하면 admin 계정으로 접속 가능하다.

step 2 - 
* /admin의 코드를 보면 다음과 같다. banlist = ["'","\"","\\","@","-","?",".","%","[","]","o"," ","c","s","p","h","s","t","u","x",":"]를 우회하여 url에 /flag에 접속할 수 있게끔해야 한다.
    ```python
    url = request.args.get('url')
    if not url:
        return "admin page", 400
    
    if any(bad in url.lower() for bad in banlist):
        return "blocked", 403

    try:
        result = subprocess.check_output(
            ['curl', url],
            stderr=subprocess.STDOUT,
            timeout=5
        )
        return result.decode('utf-8')
    except subprocess.CalledProcessError:
        return f"ERROR", 500
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 504
    ```
* localhost가 검열대상이므로 127.0.0.1의 다른 표현을 쓸 수 있다. "."과 "x"가 차단되었기에 8진수 표현으로 url = 017700000001/flag 를 사용하면 된다. 또는 10진수 변환한2130706433/flag를 사용해도 된다.

* 만약 localhost/flag로 접근하지 않고 /flag를 url에 쓰면 어떨까?
    * curl은 인자로 주어진 문자열을 보고 이것이 URL인지 파일 경로인지를 판단한다.
    * curl http://127.0.0.1/flag는 http:// scheme이 있으므로 http 프로토콜로 요청한다. 
    * curl /flag 는 scheme이 없으므로 로컬 파일 경로로 해석한다. /flag라는 파일을 현재 서버 파일시스템에서 찾는 것이다. 017700000001는 IP 주소를 표기한 것으로 curl이 이를 호스트명으로 인식하기에 http 요청 경로가 되는 것이다.

## 결과
admin 쿠키를 가지고 url에 localhost/flag를 잘 우회하여 get 요청을 보내면 된다.

