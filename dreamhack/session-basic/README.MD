# Challenge: dreamhack - session-basic

## 문제 설명 & 접근
쿠키와 세션으로 인증 상태를 관리하는 간단한 로그인 서비스라고 나와있다.
admin 계정으로 로그인에 성공하면 된다.

주어진 app.py를 열어보면 이전의 cookie 문제와 유사하다. "/" 코드를 보면 쿠키의 sessionid를 가져와서 session_storage에서 조회하고 username이 admin이라면 flag를 출려갛는 구조다.


## 문제 풀이
Step 1
* flask 웹서버 코드
    * admin 세션 id를 만들고 session_storage 딕셔너리에 저장한다. 즉, 클라이언트로 접속했을 때 session_storage에는 admin에 대한 내용이 들어가 있다.
    ```python
    if __name__ == '__main__':
        import os
        # create admin sessionid and save it to our storage
        # and also you cannot reveal admin's sesseionid by brute forcing!!! haha
        session_storage[os.urandom(32).hex()] = 'admin'
        print(session_storage)
        app.run(host='0.0.0.0', port=8000)
    ```

* "/login" 부분을 보면 마찬가지로 session_id를 만들고 session_storage 딕셔너리에 관련 정보를 저장한다. 알려진 guest, guest로 로그인한 다음, 쿠키를 바꾼다면, 이미 생성된 admin의 session_id를 알아내면 된다.
    ```python
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            try:
                # you cannot know admin's pw
                pw = users[username]
            except:
                return '<script>alert("not found user");history.go(-1);</script>'
            if pw == password:
                resp = make_response(redirect(url_for('index')) )
                session_id = os.urandom(32).hex()
                session_storage[session_id] = username
                resp.set_cookie('sessionid', session_id)
                return resp
            return '<script>alert("wrong password");history.go(-1);</script>'
    ```
* "/admin" 부분을 보면 session_storage 딕셔너리를 return한다. 따라서 /admin으로 접속한다음, admin의 sessionid를 탈취하면 된다. "/admin" 부분의 일부 코드가 주석처리되면서 사용자 검증을 거치지 않아 생긴 취약점이라 볼 수 있다. (TODO) 표시가 있는 걸로 보아 나중에 할 작업으로 두었지만 고치지 않은, 즉 일부로 보안을 허술하게 설정한 상황이다.


## 결과
딕셔너리에서 탈취한 admin의 session_id로 쿠키를 변조하면 flag가 나온다.

