# Challenge: picoCTF - FLAG_HUNTERS

## 문제 설명 & 접근
Lyrics jump from verses to the refrain kind of like a subroutine call. 
There's a hidden refrain this program doesn't print by default. Can you get it to print it? There might be something in it for you.

netcat으로 연결하면 다음과 같이 나온다.

Command line wizards, we’re starting it right,
Spawning shells in the terminal, hacking all night.
Scripts and searches, grep through the void,
Every keystroke, we're a cypher's envoy.
Brute force the lock or craft that regex,
Flag on the horizon, what challenge is next?

We’re flag hunters in the ether, lighting up the grid,
No puzzle too dark, no challenge too hid.
With every exploit we trigger, every byte we decrypt,
We’re chasing that victory, and we’ll never quit.

Crowd: 

코드 파일을 열어봐야할 것 같다.

## 필요한 개념
#### 정규표현식(regex)
* 정규표현식은 문자열 검색, 일치 여부 검사 등을 수행하는 패턴 기반 규칙
* re.match(r"\w+@\w+\.\w+", "test@email.com") <- 이런 식으로 사용한다.
* 패턴(r"~"의 큰따옴표 안 부분)이 CROWD면 문자열이 정확히 "CROWD"로 시작되어야 한다.
* 패턴이 CROWD.*이면 CROWD 뒤에 뭐든지 0개 이상 가능하다는 의미이다. 
* 만약 CROWD* 이면 고정 문자열 CROW에 D*, 즉 문자 D가 0개 이상 반복되어야 한다는 의미이다.
* re.match(r"RETURN [0-9]+", line): 는 문자열이 반드시 RETURN과 공백 뒤에 0부터 9까지의 숫자 하나 이상 있어야 한다는 의미


## 문제 분석
* 주어진 lyric-reader.py의 코드를 열어보면 가사를 출력하는 코드이다.
* flag가 포함된 secret_intro 문자열에 [REFRAIN]이라는 후렴구와 [VERSE1]이라는 벌스 부분 등의 가사 부분을 덧붙여져 있다.
* 코드를 뜯어보면, 가사를 [VERSE1]부터 쭉 출력하다가 REFRAIN; 부분을 만나면 [REFRAIN] 부분에서 후렴구 부분을 출력하고 다 출력하면 마지막의 RETURN 부분을 만나 원래 가사로 돌아가는 구조이다.
* REFRAIN을 만나면, 해당 라인의 다음 줄을 REFARIN의 마지막에 있는 "RETURN 라인번호"로 저장하고 RETURN에 도달했을 때 라인번호를 추출해 되돌아가는 코드이다.
* 처음 시작했을 때 벌스 부분부터 출력하고 후렴구를 건너가서 후렴구에 CROWD : 에서 사용자 입력을 받고 가사를 수정하므로 해당 부분을 이용해 RETURN 0을 집어넣는다면 숨겨진 secret_intro로 건너뛰어 출력할 것이다.


## 문제 풀이
바로 RETURN 0을 입력하면, 코드의 CROWD.* 부분에 막혀 그대로 CROWD가 앞에 있는 한 문장으로 처리가 되므로 가사 출력만 될 뿐 코드 점프에 영향이 안간다.

따라서 처음에 라인에서 세미콜론으로 한번 더 문장을 쪼갠다는 점을 이용하자.
; RETRUN 0 을 입력하니 또 그대로 출력만 되고 secret_intro 쪽으로 점프하지 않는다.

RETURN 정규식 처리가 맨 앞에 공백이 없으므로 공백도 지운
;RETRUN 0 을 입력해주면 secret_intro로 점프하여 flag를 가져온다. SQL인젝션과 비슷한 느낌

## 결과
picoCTF{70637h3r_f0r3v3r_250bd6ef}
