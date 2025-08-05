# Challenge: dreamhack - simple_sqli

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/268


## 추가 학습
* app.py의 get_db 함수가 왜 있는가?
    ```python
    def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db
    ```
    * g는 flask에서 제공하는 request context의 일부로, 한 요청이 처리되는 동안 유지되는 임시 저장공간이다. 이 객체에 사용중인 db 연결이 있는지 확인하고, 없으면 sqlite3.connect로 db를 연결한다.
    * 요청 처리하면서 db 연결을 매번 연결-해제는 비용이 크므로 한 요청 내에서는 동일한 DB 연결을 재사용하는 코드이다.
* app.py의 query_db는 뭘 위한 함수인가?
    ```python
    def query_db(query, one=True):
        cur = get_db().execute(query)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    ```
    * get_db로 db연결을 얻은 다음, SQL 쿼리를 실행하는 함수이다. fetchall을 통해 결과를 리스트 형태로 저장
    * cur는 .execute(query)로 쿼리를 실행하면 결과를 탐색할 수 있게 해주는 임시 객체이다. fetchall을 쓰면 쿼리 결과로 나온 행들을 리스트로 반환한다. db.row_factory=sqlite3.Row로 지정했으니 리스트 각 요소는 딕셔너리처럼 열이름으로 접근가능한 Row 객체이다.
    * one의 기본값이 True이므로 one=False로 호출하지 않는 이상 첫 행만 가져온다.

* app.py의 close_connection 코드
    ```python
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
    ```
    * flask는 하나의 요청이 끝나면 teardown_appcontext로 등록된 함수를 호출한다. db 연결이 열려였으면 리소스가 낭비되므로 요청이 끝나면 연결을 해제한다. 즉, 요청 후처리를 위한 코드이다.

## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. 데이터베이스 초기 세팅 코드를 보면 guest의 비밀번호는 guest이고 admin은 랜덤하게 생성한 16바이트 문자열이다.
* 로그인 코드를 보면 폼에 입력된 userid와 userpassword를 그대로 집어넣은 쿼리문을 만들어 일치하는 회원 정보를 가져온다. userid가 admin인 것을 검증한 다음, flag를 출력하는 것을 알 수 있다.
* 사용자가 입력한 값을 검증하는 코드가 없으므로 sql injection 취약점이 발생한다.


step 2
* userid 부분에 간단하게 admin" -- 를 입력하면 userid가 admin이고 비밀번호 검증 쪽은 주석처리되면서 admin 계정으로 로그인 가능하다.
* 또는 userid와 userpassword 검증이 and로 묶여있으니, userid에 admin을 입력한 다음(참), userpassword에서 뒤에 참인 or 조건을 넣으면 모든 userid 값을 조회 가능하다. or w조건에 userid="admin"로 조건을 엄격하게 넣으면 admin 계정으로 로그인 가능하다.



## 결과
* admin 계정으로 우회하여 로그인하면 flag가 나온다.