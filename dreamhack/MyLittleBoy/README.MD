# Challenge: dreamhack - My Little Boy

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/2204


## 추가 학습


## 문제 풀이
step 1
플래그를 얻기 위해서는 pet의 age가 10이상이어야 하는 것을 알 수 있다. 하지만 age가 올라가는 속도가 너무 느리다. /dev/boost를 이용해 tick_interval을 줄이자.

문제는 tick_interval을 줄이면 pet의 관리가 되지 않아 바로 Pet이 사망한다는 것이다. 따라서 pet의 관리도 자동화해주는 코드가 필요하다.

두 조건을 만족하는 코드를 exploit.py에 작성했다.

## 결과
* exploit.py를 동작시키면 age가 빠르게 올라가면서 flag를 얻을 수 있다.