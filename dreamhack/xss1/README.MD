# Challenge: dreamhack - xss1

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/28/


## 추가 학습
* Headless 브라우저는 일반적인 브라우저에서 UI 없이 동작하는 것을 의미한다. 눈에 보이지는 않으나 실제 웹 랜더링이나 자바스크립트 실행은 동일하게 처리된다.
* 주어진 코드에서 selenium은 xss 공격자가 만든 페이지를 가상의 admin bot이 열었을 때 생기는 취약점을 다루기 위한 용도 (시뮬레이터)
* Selenium에서 driver.add_cookie()가 요구하는 포맷을 맞춰줘야 한다. 따라서 쿠키 딕셔너리를 app.py의 해당 코드와 같이 설정한다.
* url 인코딩은 브라우저가 디코딩한다. 

## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. /flag에 get 요청을 보내면 flag.html을 랜더링하주고 post 요청을 보내면 진짜 flag 값을 담은 쿠키와 폼에서 제출한 param의 값을 check_xss에 넘긴다.
* check_xss는 param 값을 URL 인코딩하여 url 형태를 만든다. quote는 특수문자와 같은 URL에 직접 쓸 수 없는 문자를 변환해준다.
    ```python
    def check_xss(param, cookie={"name": "name", "value": "value"}):
        url = f"http://127.0.0.1:8000/vuln?param={urllib.parse.quote(param)}"
        return read_url(url, cookie)

    ```
* read_url은 관리자 권한이 있다고 가정한 headless 브라우저가 특정 url에 접속해 "http://127.0.0.1:8000/"에 접속해 쿠키 딕셔너리를 넣는다. 쿠키를 가진 상태로 위 url로 접속하게 된다. 
* /vuln에서는 내용 검증도 하지 않고 사용자 입력 그대로 출력하므로 vuln?param=```<script>alert(1)</script>```로 입력하면 xss가 발생한다. 이와 반대로 /memo에서는 내용 검증은 하지 않지만 render_template을 사용하므로 xss가 발생하지 않는다.


step 2
* 취약점은 /vuln에서 발생한다. 이 비교군인 /memo로 쿠키 정보를 넘기게 만들면 쿠키를 얻을 수 있다. 또는 다른 웹서버를 통해 얻을 수도 있다.
    ```javascript
    <script>location.href = "/memo?memo=" + document.cookie;</script>
    ```


## 결과
* /flag의 폼에 위 스크립트를 입력해서 제출하면 /memo에 플래그 정보가 기록되어 나온다.