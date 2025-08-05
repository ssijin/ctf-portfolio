# Challenge: dreamhack - baby-linux

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/837

echo $()에서 빈칸에 명령어를 입력해 flag를 찾는 문제로, flag.txt를 출력하라고 되어 있다.

## 문제 풀이
* "hi" 뒤의 ;ls 를 붙여서 출력하니 dream, hint.txt 등이 출력된다.
* cat으로 hint.txt를 열어보니 flag.txt의 경로가 나와있다.
* "hi" cat dream/hack/hello/flag.txt 를 입력하니 result가 No!로 나온다. flag.txt의 존재까지 확인한 이후이므로, 필터링이 되어있는 듯하다.
* 주어진 코드 app3.py를 열어보니 역시 flag에 대한 필터링이 되어있다. 따라서 flag.txt를 fl*g.txt 이런식으로 처리하여 작성하면 풀린다.
---
* user_input에 똑같이 입력해서 post를 해도 같은 결과가 나온다.


## 결과
flag.txt 내용 출력하면 flag가 나온다.