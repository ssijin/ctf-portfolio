# Challenge: dreamhack - mango

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/90
데이터베이스에 저장된 플래그를 획득하는 문제이다. 코드가 express와 MongoDB를 사용하는 NoSQL 문제로 보인다.

## 추가 학습
* filter 함수
    ```javascript
    filter = function(data){
        const dump = JSON.stringify(data).toLowerCase();
        var flag = false;
        BAN.forEach(function(word){
            if(dump.indexOf(word)!=-1) flag = true;
        });
        return flag;
    }
    ```
    * 입력값인 data를 문자열로 바꾸고 소문자 처리한 값이 dump. 즉, 대소문자 구별 없이 검사하기 위한 코드이다.
    * BAN 배열의 각 단어 word에 대해 함수를 돌린다. 즉, BAN 안의 금지 단어를 필터링하는 코드이다.

* req.query는 URL 쿼리스트링을 객체 형태로 담아주는 것으로 /login?uid=guest&upw=guest 요청을 보내면 { uid: "guest", upw: "guest" } 처럼 키-값 객체를 준다.
* 비구조화 할당 문법 : 자바스크립트에서 객체나 배열에서 원하는 값을 꺼낼 수 있다. 해당 문법을 사용하면 user 객체에서 uid, upw라는 이름의 값을 꺼내 같은 이름의 변수로 만든다.
    ```javascript
    const user = { uid: "guest", upw: "guest" };
    const { uid, upw } = user;
    ```
* 정규표현식
    * 점(.)은 임의의 문자 1개를 의미한다. ad.in 의 경우, 길이가 5인 문자열 중에 처음 두 글자가 ad, 네번째와 5번째 글자가 in인 문자열과 매칭된다. 따라서 admin은 매칭되고 adin이나 addddin은 매칭되지 않는다. 만약 여러 문자를 한 번에 매칭하고 싶다면 ad.{4}in 나 ad.*in 처럼 쓸 수 있다.




## 문제 풀이
step 1
* main.js를 열어보자. node.js express 웹서버에서 get /login 요청을 처리하는 함수가 있다. URL 쿼리스트링을 넘겨 필터링을 먼저 수행한다.
* mongoDB의 user collection에서 uid와 upw와 일치하는 정보를 찾아 res.send로 uid 값을 보내는 걸 알 수 있다.

step 2
* 서버에 접속해보면 '/login?uid=guest&upw=guest'의 힌트가 나와있다. 똑같이 입력하면 guest가 출력되면서 guest의 upw가 guest인 것까지 확인 가능하다. admin을 uid에 입력하면 역시 필터링에 걸린다. 로그인에 성공했을 때 이용자의 uid만 출력하니, 타입 검증을 하지 않는 점을 이용하여 blind NoSQL을 시도해보자.
* 우선 admin 비밀번호가 flag라 했으니 uid에는 ad.in, upw에는 ^D의 정규표현식을 넣어서 admin이 출력되는지를 확인해보자. 다음과 같이 입력하니 admin이 출력된다. 따라서 blind NoSQL 코드를 작성해 플래그의 값을 하나씩 알아내는 방식을 택하자. 
    ```
    http://host8.dreamhack.games:23610/login?uid[$regex]=ad.in&upw[$regex]=^D
    ```
* 앞에서부터 순차적으로 탐색하는 방식이라 굳이 길이를 알아낼 필요가 있나 싶지만, 조회는 아래와 같은 코드로 해보면 된다. 찾아보면 36글자임을 알 수 있다.
    ```javascript
    http://host8.dreamhack.games:23610/login?uid[$regex]=ad.in&upw[$regex]=^.{50,}$
    ```

step 2
* login에 보낼 스트링은 다음과 같은 구성으로 보낸다. uid는 ad.in을 설정하고 upw는 DH{1, DH{12, 이런 정규표현식이 가도록 설정한다. 주의할 점은 아래 표현식에 .이 아니라 H를 사용해 DH{ 를 쓴다면 위 필터링에 걸려 오류가 난다. main.js의 출력에서 DH{}만 반복되어 출력된다. 왜 에러가 나는지 정규표현식만 뒤져보다가 직접 서버에 입력해보고 알았다. 한참 걸렸다..
    ```python
    f"{host}/login?uid[$regex]=ad.in&upw[$regex]=D.{{{flag}{ch}"
    ```
* 후보군 character를 flag에 붙여 정규표현식 검증하면서 flag를 갱신해나가면 된다.


## 결과
* 변경된 비밀번호를 입력해, admin과 123으로 로그인하면 admin 계정으로 로그인되면서 플래그를 얻을 수 있다.