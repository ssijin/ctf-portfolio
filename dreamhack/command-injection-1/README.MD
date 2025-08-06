# Challenge: dreamhack - command-injection-1

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/44


## 추가 학습
* subprocess는 python에서 외부 명령어를 실행하고 제어할 수 있게 해주는 표준 라이브러리이다. 셸 명령어를 실행하고 결과를 가져올 때 주로 사용한다.
* subprocess.check_output()으로 주어진 명령어를 실행하고 표준 출력을 바이트 형태로 반환한다. 비정상 종료되면 CalledProcessError를 발생시킨다.

## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. request.form.get('host')를 통해 사용자가 입력한 값을 가져오고 그걸로 ping 명령어 cmd를 구성한다. subprocess.check_output으로 쉘 /bin/sh를 실행해 -c 옵션으로 cmd 명령어를 실행한다. 그리고 해당 결과를 utf-8 디코딩하여 랜더링해 반환하는 코드이다.

step 2
* app.py 코드에 의해 단순하게 8.8.8.8을 입력하고 ;를 활용해 손쉽게 command injection으로 끝나는 줄 알았으나..
* 입력했을 때 "요청한 형식과 일치시키세요."라는 문구가 뜨며 제출되지 않는다. 개발자 도구를 열어보니 다음과 같이 패턴이 설정되어 있다. 영어와 숫자로 이루어져야 하며 글자수 제한이 5~20이다.
    ```html
    <input type="text" class="form-control" id="Host" placeholder="8.8.8.8" name="host" pattern="[A-Za-z0-9.]{5,20}" required="">
    ```
* 필터링이 서버 단이 아니라 클라이언트단에서 이루어지므로 개발자도구로 우회 가능하다. 패턴을 지우고 host에 8.8.8.8"; ls # 를 입력해 제출하면 app.py, flag.py, requirements.txt, static, templates의 구성임을 알 수 있다.
* 8.8.8.8"; cat flag.py # 를 입력하면 flag가 나온다.



## 결과
* 패턴을 지우고 command injection을 수행하면 flag가 나온다.