# Challenge: dreamhack - Test-Your-Lock

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1955/
웹서버에 Results will be revealed in 10 seconds라 나와있다.
개발자도구로 Elements를 보니 10초 대기가 클라이언트에서 발생한다는 것을 알 수 있다.
서버 코드인 app.py가 주어져 있다.

## 추가 학습
* 튜플 언패킹으로 범위 생성
    * "*"를 사용해 튜플 언패킹하고 random.randint로 랜덤한 숫자를 생성하는 방법도 있다.
    ```python
    NUMBER_RANGE = (0, 10000)
    TARGET_NUMBER = random.randint(*NUMBER_RANGE)
    ```


## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. 폼 데이터에서 guess 필드 값을 가져와 TARGET_NUMBER와 비교하고 맞으면 flag를 응답하는 간단한 코드이다. 연속 요청에 대한 제한도 없고 TARGET_NUMBER의 주기적 변경이 없어 브루트포스로 끝낼 수 있어 보인다.

step 2
* 개발자 도구에 폼 데이터를 0부터 10000까지 보내는 브루트포스를 작성한다. 해당 코드는 bruteforce.js 파일에 있다.


## 결과
* 브루트포스 중 alert가 뜨면서 플래그가 출력된다.