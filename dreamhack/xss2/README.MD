# Challenge: dreamhack - xss2

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/268


## 추가 학습
* innerHTML로 단순히 script 태그를 삽입하는 것만으로 xss가 일어나지는 않는다. 하지만 innerHTML로 이미지 태그 등을 삽입하면서 이벤트 핸들러 속성에 자바스크립트를 넣으면 코드가 실행되므로 xss 취약점이 생긴다. 

## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. xss1과 거의 유사하다. 단, xss1에서는 /vuln에서 param을 그대로 출력하는 것이 아니라 vuln.html을 render_template으로 랜더링한다. 따라서 xss1처럼 memo로 document.cookie 값을 보내는 스크립트를 입력해도 xss가 발생하지 않는다.
* vuln.html을 열어보면 다음과 같은 코드가 있다. location.search로 현재 페이지의 URL 쿼리 스트링을 가져와서 URLSearchParams로 쿼리 문자열을 파싱한다. param의 값을 추출해서 id가 vuln인 div요소의 html 컨텐츠로 삽입하는 코드이다.
    ```javascript
    {% block content %}
    <div id='vuln'></div>
    <script>var x=new URLSearchParams(location.search); document.getElementById('vuln').innerHTML = x.get('param');</script>
    {%  endblock %}
    ```
step 2
* 단순 script 태그가 아니라 img 태그를 이용하자. 존재하지 않는 경로를 주고 이미지 로딩에 실패했을 때의 onerror 이벤트를 넣어주면 쿠키를 탈취할 수 있다.
    ```
    <img src="wrong" onerror="location.href='/memo memo='+document.cookie">
    ```


## 결과
* /flag의 폼에 위 스크립트를 입력해서 제출하면 /memo에 플래그 정보가 기록되어 나온다.