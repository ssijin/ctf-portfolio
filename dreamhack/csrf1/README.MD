# Challenge: dreamhack - csrf1

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/26


## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. xss1과 거의 유사하다. 차이는 /vuln의 수정과 /admin/notice_flag가 새로 등장했다는 점이다.
* /vuln은 사용자가 전달한 param에 대해 소문자 처리 후, 키워드 필터링을 진행한다. frame, script, on의 키워드를 *로 치환한 다음 param을 return하는 코드이다.
* /admin/notice_flag를 보자. 접속한 클라이언트 IP 주소가 로컬호스트, 즉 서버 자신이어야 하며 userid를 admin으로 접근해야 /memo에 flag를 작성한다. 간단한 인증/access control 로직으로 볼 수 있다.

step 2
* 그렇다면 필터링 된 세 가지 키워드를 제외한 다른 키워드를 이용해야 한다. 또한 로컬호스트여야 한다는 조건이니 CSRF로 관리자가 /admin/notice_flag에 userid="admin"의 요청을 보내도록 해야 한다. 
    ```javascript
    <img src="/admin/notice_flag?userid=admin" />
    ```

## 결과
* /flag의 폼에 위 스크립트를 입력해서 제출하면 /memo에 플래그 정보가 기록되어 나온다.