# Challenge: dreamhack - My-Best-Friend

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1859


## 추가 학습
* Express에서 HTTP 요청 처리
    * app.use(express.json());은 Content-Type이 application/json인 요청의 본문을 파싱해 JSON 문자열을 javascript 객체로 변환하고 req.body에 저장하는 미들웨어 설정
    * app.use(express.urlencoded({ extended: true }));은 Content-Type이 application/x-www-form-urlencoded인 요청을 파싱해 HTML 폼 데이터를 javascript 객체로 변환해 req.body에 저장하는 미들웨어 설정

* private api 설정
    * "::1"은 IPv6에서의 localhost이다. 즉, 자기 자신-로컬 서버를 가리킨다. 외부에서 직접 curl http://target-server.com:3000/api?admin=1와 같이 접근하는 것을 차단한다.
    ```javascript
    app.get('/api', (req, res) => {
    if (req.ip !== '::1') return res.send('No');

    ...
    return res.send(`${req.query.msg} ❤️`);
    });
    ```
* axios는 Node.js의 HTTP 클라이언트 역할을 수행한다. axios의 URL 정규화를 이용할 수 있다.

## 문제 풀이
step 1 - 내 풀이
* server.ts의 코드를 뜯어보자. /greet의 msg 부분에 "1&admin=1"이 들어가면 중복 파라미터에 의해 파싱 결과는 다음과 같다. Number로 변환하면 NaN으로 0과 다르다는 조건을 만족해서 플래그를 얻을 수 있다.
    ```
    {
        msg: '1',
        admin: ['1', '0'] 
    }
    ```
* 문제는 admin을 필터링한다는 것이다. 따라서 폼에 "1&ad	min=1"로 사이에 탭(진짜 탭)을 넣어 전송하면 필터링은 "1&ad\tmin=1"로 우회하고 axios의 정규화에 의해 \t가 없어지면서 성공!


step 2 - Intended Solution - https://dreamhack.io/wargame/writeups/27664
* express 모듈은 qs 모듈을 활용해 url query를 파싱하는데 qs 모듈은 parameterLimit: 1000로 설정되어 있다. 즉, 1000개 넘게 파라미터를 넣으면 msg 뒷 부분에 붙는 admin=0이 무효화된다는 것이다. req.query.admin이 정의되지 않았으니 Number를 거치면 NaN이 되고 조건문을 통과한다.
* 길이 제한이 없다는 것을 이용해  ```{ msg: `test${'&q=1'.repeat(1000)}` }``` 이걸 post하면 된다..


## 결과
* xss-filtering-bypass 부분으로 정규화나 인코딩 우회 부분을 학습한 것이 큰 도움이 되었다. "1&ad	min=1"를 입력하면 플래그가 나온다.
* step 2의 풀이처럼 파라미터 1000개를 입력해도 플래그가 나온다.