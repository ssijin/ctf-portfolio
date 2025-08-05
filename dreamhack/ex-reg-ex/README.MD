# Challenge: dreamhack - ex-reg-ex

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/834

정규표현식을 맞추는 예제이다.

## 문제 풀이
* 주어진 app 4.py를 확인해보면 m = re.match(r'dr\w{5,7}e\d+am@[a-z]{3,7}\.\w+', input_val) 에 해당하는 정규표현식을 작성하면 된다.
* 따라서 주어진 정규표현식 조건에 맞춰 drwwwwwwe7am@bbbb.com 의 식으로 입력


## 결과
 Input: drwwwwwwe7am@bbbb.com 를 입력하면 된다.