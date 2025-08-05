# Challenge: dreamhack - cookie

## 문제 설명 & 접근
쿠키 인증 상태를 관리하다는 간단한 로그인 서비스라고 나와있고, app2.py에 간략하게 코드가 제시되어 있다.

## 문제 풀이
* users에 guest와 admin이 등록되어 있다. guest - guest, admin - 플래그
* 로그인 쪽 코드를 보면 users에 있는 계정으로 로그인 성공 시, username으로 쿠키를 등록하고 리다이렉션한다.
* 그리고 index 함수를 보면 쿠키의 username이 admin인지 검증하고 admin이 맞다면 플래그를 출력해주고 있다.
* 이미 ID, PW를 알고 있는 guest 계정으로 로그인하고 username 쿠키의 value를 admin으로 바꿔주면 admin 검증에 성공해 플래그를 얻을 수 있다.
* 즉, "/" 경로에서 username 변수가 요청에 포함된 쿠키에 의해 결정되는 구조인데, 쿠키는 사용자가 조작할 수 있으니 계정 탈취가 가능하다.

## 결과
개발자 도구에서 cookie 값을 변경해주면 flag가 나온다.