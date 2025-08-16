# Challenge: dreamhack - pathtraversal

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/12


## 추가 학습
### 데코레이터 함수
* 데코레이터는 기존 함수나 클래스의 기능을 수정하거나 확장하는 함수이다. 원본 코드 수정 없이 부가 기능을 추가 가능해 코드 재사용성이나 가독성이 향상된다.
* 아래 internal_api는 다른 함수를 감싸는 데코레이터 함수이다. 이 함수는 원본 함수 func를 받아 보안 기능이 추가된 새로운 함수를 반환한다.
```python
def internal_api(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.remote_addr == '127.0.0.1':
            return func(*args, **kwargs)
        else:
            abort(401)
    return decorated_view
```
    * @wraps(func)는 원본 함수의 메타데이터를 보존하는 데코레이터
    * def decorated_view(*args, **kwargs):로 내부 함수 정의
    * request.remote_addr, 즉 요청을 보낸 클라이언트의 IP 주소가 localhost인지 확인한다.
    * 데코레이터를 적용하는 예시를 보자. 아래 코드는 사용자가 /api/flag에 접근하면 internal_api 데코레이터가 먼저 실행되면서 IP 주소가 127.0.0.1인지를 확인한다. 성공하면 flag()가 실행되고 실패하면 abort(401) 에러가 뜬다.
    ```python
    @app.route('/api/flag')
    @internal_api
    def flag():
        return FLAG
    ```

### windows.onload 이벤트
* window.onload = function() {//페이지가 완전히 로드된 후 실행}
* HTML 파싱 -> CSS 로드 -> 이미지 로드 -> 모든 리소스 로드 완료 -> window.onload 실행

### addEventListener
* element.addEventListener(event, function, options);
* event는 이벤트 타입(문자열), function은 실행할 함수이다.
* 아래의 코드는 ID가 form인 HTML 요소를 찾아 이벤트 리스너를 등록한다. 폼 제출 이벤트를 감지하면 user라는 함수를 실행한다.
```html

<form id="form" method="POST" action="/get_info">
    <input type="text" id="userid" name="userid" placeholder="사용자 ID">
    <button type="submit">제출</button>
</form>

...

<script>
document.getElementById('form').addEventListener('submit', user);
</script>
```

## 문제 풀이
burp suite를 통해 userid=../flag 를 post하면 flag가 출력된다.

## 결과
