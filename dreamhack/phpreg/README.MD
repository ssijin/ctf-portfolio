# Challenge: dreamhack - phpreg

## 문제 설명 & 접근
웹으로 접근해보면 nickname과 password를 입력하게 되어있다.
description을 보면 적절히 입력해서 Step 2로 넘어가고 system() 함수를 이용하여 플래그를 획득하라고 되어 있다. 
플래그는 ../dream/flag.txt에 위치한다고 한다.

## 문제 풀이
step 1
* 주어진 php 파일을 열어보면, 다음과 같이 필터링한다. 소문자 알파벳이나 대문자 알파벳 중 하나라도 매치되면 true이므로 필터링된다.
    ```php
    if (preg_match("/[a-zA-Z]/", $input_pw)) {echo "alphabet in the pw :(";}
    ```
* preg_replace 쪽을 보자. input_name에서는 nyang 문자열을 대소문자 무시하고 제거한다.
* input_pw에서이 패턴을 순서대로 나열하면 다음과 같다. 다음 패턴을 찾아 d4y0r50ng로 교체하는 것이다. 예시로는 "1@12319!"
    * 숫자0개이상
    * @
    * 숫자 2~3개 
    * 31을 한번 이상 반복 
    * 0~8, "를 제외한 문자 하나 (위 if 문에 의해 영문자도 제외해야한다)
    * !
    ```php
    $name = preg_replace("/nyang/i", "", $input_name);
    $pw = preg_replace("/\d*\@\d{2,3}(31)+[^0-8\"]\!/", "d4y0r50ng", $input_pw);
    ```
* 필터링을 거친 결과가 if ($name === "dnyang0310" && $pw === "d4y0r50ng+1+13") 이 조건문을 만족하면 된다.
* 따라서 id 쪽에 dnnyangyang0310, pw에 1@12319!+1+13 을 입력해주자. id는 nyang 부분이 소거되니 소거된 이후에 nyang 부분이 유지되게끔 nnyangyang의 형식을 사용
* step 1 해결
---

step 2
command를 입력하게끔 되어 있다.
* 코드를 보면 flag를 입력하면 대소문자 구분없이 차단하게끔 필터링되어 있다.
    ```php
    else if (preg_match("/flag/i", $cmd)) {
                  echo "<pre>Error!</pre>";
    }
    ```
* 해당 command에 입력한 값을 system($cmd)로 실행 결과를 출력하게 되어 있다. system은 php에서 쉘 명령어를 실행하는 함수이다. command 입력에 ls를 집어넣으니 index.php와 step2.php가 나온다.
* 결국 flag 언급없이 ../dream/flag.txt를 열람해서 flag를 알아야 한다. cat ../dream/f*.txt를 입력하면 flag가 나온다.


## 결과
* step 1은 id 쪽에 dnnyangyang0310, pw에 1@12319!+1+13 을 입력
* step 2은 cat ../dream/f*.txt 입력