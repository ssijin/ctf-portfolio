# Challenge: dreamhack - CSP-bypass-Advanced

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/436/



## 추가학습
### Jinja2 템플릿에서 | safe 필터의 의미
* safe가 없을 때 Jinja2는 기본적으로 XSS 방어를 위해 HTML 이스케이프를 수행한다.
<!-- 입력: <script>alert('XSS')</script> -->
<!-- 출력: &lt;script&gt;alert('XSS')&lt;/script&gt; -->

* safe 필터를 사용하면 HTML 이스케이프를 비활성화하여 원본 HTML을 그대로 랜더링한다.
<!-- vuln.html -->
{{ param | safe }}

<!-- 사용자 입력: <script>alert(1)</script> -->
<!-- 브라우저에서 보이는 HTML: -->
<script>alert(1)</script>

<!-- 결과: 스크립트 실행됨! -->

### 

## 문제 풀이
step 1
*