# Challenge: dreamhack - Really Not SQL

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/2105
json을 이용하는 문제로 보인다. SQL 언급 때문에 인젝션이나 인증에 꽂혀 삽질했다.
구성은 src와 .htaccess, 000-default.conf, flag, run.sh이며, src 안에 login.php가 있다.

## 추가학습
* session_start()는 php의 세션 기능을 다루는 함수이다. 이 함수가 실행되면, 브라우저에 phpsessid가 생성되며 서버에서 이 세션에 데이터를 저장할 수 있다.
* .htaccess : 아파치 웹서버의 디렉터리별 접근 권한, 옵션 등을 설정하는 파일이다.
    * 아래의 코드는 웹서버가 delete 요청을 받았을 때 해당 요청을 모두 거부해 실행을 차단하는 코드이다.
    ```
    <Limit DELETE>
        Require all denied
    </Limit>
    ```
* 000-default.conf는 아파치 서버 전체의 기본 설정을 담당한다. .htaccess나 000-default.conf가 잘못 설정되어 있다면 인증 없이 파일 리스트가 노출되거나, 웹 DAV 활성화 및 디렉터리 인덱싱이 허용되는 취약점이 생길 수 있다.
    * 웹DAV(Web Distributed Authoring and Versioning)는 웹 서버에 파일을 웹을 통해 직접 업로드, 수정, 삭제할 수 있게 해주는 프로토콜이다. 아파치 설정에 DAV On이 되어 있으면, 웹DAV 클라이언트로 파일을 업로드/수정할 수 있다.

## 삽질
* 주어진 login.php 파일부터 열어봤다. 폼에서 입력한 username과 password를 가져와 username이 붙은 json 파일 경로를 만든다. 사용자는 admin과 guest 둘만 가능하다. username이 이 둘 중 한 명이면 그 계정의 json 파일을 읽어와 username과 password를 조회하는 코드이다. json 파일의 비밀번호가 SHA256 해시로 변환된 것까지 확인 가능하다. 로그인 성공하면 &_SESSIOM['user']로 권한도 관리한다.

* 코드 상 path traversal이 가능해보였으나, 그 아래 코드에서 username이 admin과 guest로만 한정되어 불가능했다.
    ```php
    $filename = $username . '.json';
    $filepath = $userDir . $filename;
    ```
* SHA256 복호화도 당연히 비현실적이다. 그런데 풀이 중 guest의 비밀번호가 guest라는 걸 우연히 알아냈다.
* 파일 중 edit_profile.php가 있어 비밀번호를 변경하는 문제인가 싶었지만 세션에 admin이 등록되어 있어야 했다. 세션 값을 서버에서 관리하니 당연히 개발자도구로 접근할 여지가 없어보인다.
    ```php
    if ($_SESSION['user'] !== "admin") {
        $error = "Only admin can edit user profile";
    }
    ```

## 문제 풀이
Step 1 - 000-default.conf 내용 확인
* 아래 설정은 /var/www/html/ 디렉터리에 대한 접근 권한이나 옵션을 설정한 것이다.
    * AllowOverride None은 .htaccess 파일로 상위 설정을 덮어쓸 수 없음을 의미한다.
    * Require all granted로 모든 사용자에게 접근을 허용한다.
    ```
    <Directory /var/www/html/>
        AllowOverride None
        Require all granted
    </Directory>
    ```
* 아래 설정은 /var/www/html/user/ 디렉터리에 대한 설정이다.
    * DAV On이 되어있다. 즉, 웹 DAV 기능이 활성화되어 있다는 것이다.
    * Options Indexes로 디렉터리 인덱싱을 허용하고 있다. 즉, 브라우저에서 /user/로 접근하면 폴더 내 파일 목록이 노출된다.
    * AllowOverride All은 .htaccess 파일로 이 디렉터리 설정을 덮어쓸 수 있음을 의미한다.
    ```
    <Directory /var/www/html/user/>
        DAV On
        Options Indexes
        AllowOverride All
        Require all granted
    </Directory>
    </VirtualHost>
    ```
Step2 - 웹DAV로 파일 업로드/수정
* 파일 업로드/수정이 가능하니 admin의 json 파일을 수정해 내가 원하는 비밀번호로 변경한다. 로직을 보면 sha256 해시를 사용하므로 내가 원하는 비밀번호로 변경이 가능하다. guest의 비밀번호가 guest라는 것을 응용해 guest.json의 해시값으로 admin.json을 변경해주고 이를 서버측 admin.json에 덮어썼다.
* curl 명령어 사용
    curl -T ./admin.json http://서버주소/user/admin.json
    * 여기서 ./admin.json은 수정한 파일 경로이다.
* 이제 admin 계정의 비밀번호는 guest로 변경되었다. 이를 통해 로그인하고 admin 세션이 있으므로 flag.php를 실행시켜 flag값을 알아낸다.

추가풀이 
* 이전에 풀이한 image-storage 문제에서 만든 websell.php를 /user에 넣을 수 있다.
    curl -T webshell.php http://host8.dreamhack.games:18701/user/
* http://host8.dreamhack.games:18701/user/webshell.php로 접속하면 webshell을 실행할 수 있다. 


## 결과
webshell을 이용해 cat /flag를 입력하면 플래그가 나온다. 또는 admin 세션을 가지고 flag.php를 실행시키면 플래그가 나온다.