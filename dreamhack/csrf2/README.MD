# Challenge: dreamhack - csrf2

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/269


## 문제 풀이
step 1
* 처음에 문제에 접근하면 please login이 출력된다. 이는 로그인을 아직 하지 않아 session_storage에 관련 내용이 없기 때문이다. users에 guest와 admin이 있으니 guest로 로그인해보자. /login 코드를 살펴보면 session_storage에 guest에 대해 등록된다. 추가적으로 로그인이 성공하면 index로 리다이렉션하도록 하고 있다. 
* /change_password를 보자. 쿠키에 저장된 session_id를 가져와서 session_storage의 값과 비교한 뒤 맞으면 pw를 갱신하는 코드이다.


step 2
userid="admin"의 요청을 보내도록 해야 한다. 
    ```javascript
    <img src="/change_password?pw=123">
    ```

## 결과
* 변경된 비밀번호를 입력해, admin과 123으로 로그인하면 admin 계정으로 로그인되면서 플래그를 얻을 수 있다.