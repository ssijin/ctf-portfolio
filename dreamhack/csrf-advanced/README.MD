
# Challenge: dreamhack - CSRF-Advanced

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/442/



## 추가학습
### html에서 hidden의 의미
hidden 속성은 브라우저에서 화면에는 표시되지 않지만 폼 데이터에는 포함된다. 따라서 사용자가 볼 수 없지만 서버로는 전송된다. 이 문제에서는 방법 1을 사용해 csrftoken을 폼 데이터로 전송한다.
* 방법 1 : hidden 속성
    ```html
    <input type="text" value="{{ csrf_token }}" name="csrftoken" hidden>
    ```
    type="text"이지만 화면에는 숨겨져있다.
* 방법 2 : type="hidden"
    ```html
    <input type="hidden" value="{{ csrf_token }}" name="csrftoken">
    ```
    아예 hidden으로 type을 정의한 방법이다.    


### 

## 문제 풀이
Step 1 - 코드 해석
* app.py의 코드의 /login부터 보자. 아래의 코드는 폼에서 ID와 비밀번호를 받아와 검증에 성공했을 때의 코드이다.
    * 메인 페이지로 리다이렉트하는 HTTP 응답 객체를 생성한다. resp는 <class 'flask.wrappers.Response'>의 타입을 가지고 status_code, location, headers, data의 구성 요소를 가지고 있다.
    * 16자리 16진수 문자열로 session_id를 생성한다.
    * session_storage에 로그인 상태를 저장하고, CSRF 토큰을 생성한다. 사용자명과 IP 주소를 결합해 바이트로 인코딩 후 MD5 해시 계산 => 16진수 문자열로 변환
    * HTTP 응답 헤더에 Set-Cookie: sessionid=~~~로 HTTP 응답 헤더에 추가된다. 즉 브라우저에 세션 ID가 쿠키로 저장된다.
    ```python
    if pw == password:
            resp = make_response(redirect(url_for('index')) )
            session_id = os.urandom(8).hex()
            session_storage[session_id] = username
            token_storage[session_id] = md5((username + request.remote_addr).encode()).hexdigest()
            resp.set_cookie('sessionid', session_id)
            return resp 
        return '<script>alert("wrong password");history.go(-1);</script>'
    ```
    * 즉, CSRF 토큰은 username과 request.remote_addr만 알면 간단히 알아낼 수 있다.
* app.py의 /change_password 코드를 보자. 쿠키에서 sessionid를 추출해 username과 csrf_token을 검증 후 get 요청으로 보내온 pw로 바꿀 수 있다. 
    ```python
    def change_password():
        session_id = request.cookies.get("sessionid", None)
        try:
            username = session_storage[session_id]
            csrf_token = token_storage[session_id]
        except KeyError:
            return render_template("index.html", text="please login")
        pw = request.args.get("pw", None)
        if pw == None:
            return render_template("change_password.html", csrf_token=csrf_token)
        else:
            if csrf_token != request.args.get("csrftoken", ""):
                return '<script>alert("wrong csrf token");history.go(-1);</script>'
            users[username] = pw
            return '<script>alert("Done");history.go(-1);</script>'
    ```
* change_password.html을 열어보자. csrftoken이 hidden 속성으로 되어있다. 
    ```html
    <h2>Change Password</h2><br/>
    <form method="GET">
    <div class="form-group">
        <label for="InputName">new password</label>
        <input type="password" class="form-control" placeholder="new password" name="pw" required>
    </div>
    <input type="text" value="{{ csrf_token }}" name="csrftoken" hidden>
    <button type="submit" class="btn btn-default">Change Password</button>
    </form>
    ```

Step 2 - admin에 대한 코드 해석
* 해당 코드에서는 피해자를 설정하기 위해 Selenium을 이용한다. 아래 코드는 admin 계정으로 자동 로그인 후 특정 URL을 방문하여 CSRF 공격의 피해자 역할을 시뮬레이션한다.
    ```
    def read_url(url, cookie={"name": "name", "value": "value"}):
        cookie.update({"domain": "127.0.0.1"})
        service = Service(executable_path="/chromedriver")
        options = webdriver.ChromeOptions()
        try:
            for _ in [
                "headless",
                "window-size=1920x1080",
                "disable-gpu",
                "no-sandbox",
                "disable-dev-shm-usage",
            ]:
                options.add_argument(_)
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(3)
            driver.set_page_load_timeout(3)
            driver.get("http://127.0.0.1:8000/login")
            driver.add_cookie(cookie)
            driver.find_element(by=By.NAME, value="username").send_keys("admin")
            driver.find_element(by=By.NAME, value="password").send_keys(users["admin"])
            driver.find_element(by=By.NAME, value="submit").click()
            driver.get(url)
        except Exception as e:
            driver.quit()
            # return str(e)
            return False
        driver.quit()
        return True
    ```
    * 동작은 전달받은 쿠키를 브라우저에 설정하고 admin으로 자동로그인을 진행한다.
    * /login 페이지의 username 필드에 "admin"을 입력하고, password 필드에 users["admin"] 텍스트를 입력해 제출한다. 따라서 앞 내용과 합쳐보면 csrftoken은 admin127.0.0.1 에 대해 md5를 거친 것이다.

Step 3
* admin의 csrftoken을 구해서 admin 계정의 비밀번호를 변경해보자. 다음 코드를 실행하면 csrftoken을 구할 수 있다.
    ```python
    print(md5(("admin127.0.0.1").encode()).hexdigest())
    ```
* /flag 페이지의 폼에 <img src="/change_password?pw=admin&csrftoken=7505b9c72ab4aa94b1a4ed7b207b67fb">를 입력하자. 그러면 /flag에서 check_csrf를 거치면서 http://127.0.0.1:8000/vuln?param=<img src="/change_password?pw=admin&csrftoken=7505b9c72ab4aa94b1a4ed7b207b67fb"> 로 url이 만들어져 read_url을 거친다.
* read_url에서 admin 계정으로 로그인함에 따라 admin의 sessionid와 csrftoken이 만들어지고 해당 url로 접근한다. /vuln에서 "frame", "script", "on"을 필터링하고 param을 return한다. 따라서 change_password로 pw와 이미 계산해둔 csrftoken이 GET 요청에 들어가 비밀번호가 바뀐다.

## 결과
변경한 비밀번호를 통해 admin 계정으로 로그인하면 flag를 얻을 수 있다.
CSRF 토큰이 예측 가능하여 생긴 취약점이다.