# Challenge: dreamhack - secure mail

## 문제 설명 & 접근
Tool : 개발자도구

보안 메일의 비밀번호를 찾는 문제이다. 단, 보안 메일의 비밀번호가 생년월일 6자리로 파악된다고 한다.
생년월일로 구성된 6자리이므로 브루트포스도 염두에 두자.
개발자도구로 열어보니 _0x9a220 함수를 뜯어봐야한다는 것까지 알 수 있다.
```html
<button type="submit" onclick="_0x9a220(pass.value);">Confirm</button>
```

## 문제 풀이
Step 1
* 개발자도구 sources 탭에서 _0x9a220 함수를 찾아본다. 사용자가 입력한 값을 받아 입력값을 검증하는 함수인 듯하다. 난독화가 심해 브루트포스가 훨씬 빠를 것같다. 
    ```javascript
    function _0x9a220(_0x30bf04) {
        var _0x540d50 = _0x225843
        , _0x2ee89c = Array[_0x540d50('0x99', '3itY')](_0x3eebe5(_0x30bf04, null, raw = !![]))[_0x540d50('0xe2', 'G(su')](_0x66324e => _0x66324e['charCodeAt']())
        , _0x2fef58 = new _0x58829a['_0x14c3a3'][(_0x540d50('0x29', 'd%09'))](_0x2ee89c,_0x2ee89c);
        //실제로 file은 훨씬 긴 배열. README.MD에서는 구조 파악용으로 축약한다
        file = [0x68, 0xda, 0xe1, 0x1b, 0x20, 0x6e, 0xbc, 0x1f, 0x1, 0xff, 0x6f, 0x4, 0x89, 0x8a, 0x6e, 0x1d, 0x93, 0xfa, 0x6b, 0xa1, 0x56, 0x29, 0xa9, 0x8a],
        dfbora = _0x2fef58['decrypt'](file),
        odradurs1 = '';
        for (var _0x302add = 0x0; _0x302add < dfbora[_0x540d50('0xde', '@%wH')]; _0x302add++)
            odradurs1 += String[_0x540d50('0x2', 'dARo')](dfbora[_0x302add]);
        if (_0x3eebe5(odradurs1, null, raw = !![]) != _0x540d50('0x55', 'dGZC'))
            return alert('Wrong'),
            ![];
        return document['write'](_0x540d50('0x66', 'AZ$r') + odradurs1 + '\x22>'),
        !![];
    }
    ```

Step 2
* 브루트포스 로직짜기
* 우선 잘못된 값을 입력하면 alert가 설정되어 있다. 적어도 1000번은 로직을 돌려야하므로 alert를 해제해야 한다. secure-mail.html에서 alert 부분을 찾아보면 다음과 같다. 검증에 실패하면 Wrong 알림창을 띄우고 false를 반환한다는 것을 알 수 있다.
    ```javascript
    if(_0x3eebe5(odradurs1,null,raw=!![])!=_0x540d50('0x55','dGZC'))return alert('Wrong'),![];
    ```

파일을 수정한다면 return에 alert 부분을 빼고 else로 return 1을 넣어서 처리할 수도 있다. 그래도 console 탭에서 alert를 새로 덮어쓰는 방법을 택했다. 
    ```javascript
    alert = function() {};
    ```
* 이후 브루트포스 로직을 개발자도구 console에서 돌린다. 로직은 secure_mail.js에 정리한다.
* 결과로 비밀번호 960229가 나온다.

## 결과
flag에 960229를 입력하면 Img로 파일이 나온다.

