# Challenge: dreamhack - session

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/266

쿠키와 세션으로 인증 상태를 관리하는 간단한 로그인 서비스라고 나와있다.
admin 계정으로 로그인에 성공하면 된다.

## 문제 풀이
Step 1
* app.py 코드를 뜯어보자. app.py가 실행되면 admin session이 자동으로 생성되는 것을 알 수 있다. 주목해야할 점은 os.uramdom(1).hex() 부분이다. 1바이트 랜덤 데이터를 생성해 16진수 변환한 것을 세션 id로 등록하는 것을 알 수 있다.
    ```python
    if __name__ == '__main__':
        import os
        session_storage[os.urandom(1).hex()] = 'admin'
        print(session_storage)
        app.run(host='0.0.0.0', port=8000)
    ```
* session id가 256가지밖에 없으니 admin session에 대해 브루트포스로 처리할 수 있다. 해당 공격 코드는 bruteforce.py에 작성했다.

## 결과
256가지의 경우의 수로 admin의 session_id를 얻어내면 플래그를 얻을 수 있다.

