# Challenge: dreamhack - web-ssrf

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/75/
flask로 작성된 image viewer라고 한다. 플래그는 /app/flag.txt에 있다


## 추가 학습
* url 구조 : scheme://netloc/path;params?query#fragment
* urlparse를 했을 때 return되는 값은 아래와 같다.
    ```
    ParseResult(
        scheme='http',
        netloc='localhost:8000',
        path='/path/to/page',
        params='',
        query='name=alice&age=30',
        fragment='section2'
    )
    ```
* 웹 브라우저에서 이미지를 보여줄 때 서버 경로로 접근하거나 데이터 자체를 문자열로 인코딩해서 넣는 방식이 있다. 후자를 data uri scheme이라 하며, base64 인코딩을 이용해 처리할 수 있다. HTTP로 받아온 이미지 데이터는 일반적으로 바이너리 데이터이다. 이 상태로 HTML에 넣어 보이기는 어려우니 이미지를 바이너리에서 텍스트로 바꿔서 HTML에 넣기 위해 base64를 사용한다. base64.b64encode()는 바이너리를 안전한 ASCII 문자열로 바꿔주며 결과가 바이트이다. 이후, flask 템플릿에 string으로 넣기 위해 decode("utf-8")로 바꿔주면 된다. 예시는 다음과 같다. ```img = base64.b64encode(data).decode("utf8")```
* 랜더링할 때, ```return render_template("img_viewer.html", img=img)``` 으로 img를 넘겨준 후, img_viewer에서 ```<img src="data:image/png;base64, {{ img }}"/>``` 처럼 사용해주면 된다. 이 방식을 사용하면 별도의 파일을 서버로부터 추가로 다운로드하지 않아도 HTML 문서 안에 인라인으로 이미지가 표시된다.
* 서버 동시 운용
    * 로컬 HTTP 서버를 127.0.0.1 임의 포트에서 별도의 thread로 구동할 수 있다. 메인 thread에서는 flask가 0.0.0.0:8000에서 실행되어 웹 서비스를 제공한다. 두 서버를 돌려 전자는 private 파일 서버, 후자는 외부에 공개되는 flask 웹/앱 역할을 배정할 수 있다.
    * 아래 코드에서 127.0.0.1의 랜덤 포트에 http 서버를 실행하므로 외부에서 해당 서버에 직접 접근이 안되고 오직 로컬에서만 접근 가능한 private한 서버라 볼 수 있다. 핸들러로 http.server.SimpleHTTPRequestHandler를 지정했으므로 별도 코드 작성 없이 간단히 현재 작업 디렉터리 내 파일과 디렉터리 목록을 HTTP 프로토콜로 제공하는 웹 서버를 만들 수 있다. 즉, 클라이언트에서 /index.html을 요청했을 때  디렉터리에 있으면 이를 전송해준다. 반대로, flask 서버는 본인 컴퓨터의 모든 IP와 8000번 포트로 연다.
    ```python
    local_host = "127.0.0.1"
    local_port = random.randint(1500, 1800)
    local_server = http.server.HTTPServer(
        (local_host, local_port), http.server.SimpleHTTPRequestHandler
    )

    def run_local_server():
        local_server.serve_forever()

    threading._start_new_thread(run_local_server, ())

    app.run(host="0.0.0.0", port=8000, threaded=True)
    ```
    * 만약 포트 번호 없이 localhost로 접근한다면 기본적으로 80번 포트로 접속을 시도한다. 위 코드에서는 80번 포트에 어떤 서버도 열지 않으므로 연결 실패 오류가 난다.
* 127.0.0.1은 루프백 주소의 범위를 이용해 우회 접속 가능하다. 127.0.0.0/8로 네트워크 주소가 127 부분이므로 127.255.255.255까지 묶여 루프백으로 예약된 것을 알 수 있다. 또는 127.0.0.1을 16진수 변환한 7f000001 도 사용 가능하다. 
* URL에서 호스트나 스키마가 대소문자를 구분하지 않는다는 점을 이용해 LOCALhost와 같이 입력해도 같은 호스트로 인식하므로 우회 가능하다.


## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. img_viewer 함수를 보면 입력받은 url을 파싱해서 url이 /로 시작하면 http://localhost:8000을 앞에 붙여준다. 만약 localhost나 127.0.0.1이 명시적으로 있다면 error.png를 띄운다.
* 따라서 필터링을 우회해야 하고, http 서버가 포트 번호 1500~1800 임의 포트에서 돌아가므로 포트도 찾아야 한다. 범위가 주어졌으니 브루트 포스로 포트를 탐색해야 한다.

step 2
* 포트에 대한 브루트포스를 하는 findport.py를 작성한다. error.png의 base64인코딩된 부분 일부가 나오지 않을 때까지 돌리도록 로직을 구성한다. 127.0.0.2를 주소로 두고 돌렸으나, app.py에서 http 서버를 ```local_host = "127.0.0.1"```로 명시해둬서인지 계속 error.png가 뜬다. 따라서 localhost의 대소문자 구분을 이용해서 LOCALhost로 입력해서 돌리면 포트 번호를 얻을 수 있다.
* 포트번호까지 합쳐 폼에 http://LOCALhost:포트번호/flag.txt를 입력하면 된다. 여기서, 주소가 /app/flag.txt가 아니라 /flag.txt인 이유는 웹서버가 동작하는 디렉터리 경로가 /app이기 때문이다.
* 개발자도구에서 img src 부분을 base64디코딩하면 플래그가 나온다.

## 결과
* 폼에 http://LOCALhost:포트번호/flag.txt를 입력하면 플래그를 얻을 수 있다.