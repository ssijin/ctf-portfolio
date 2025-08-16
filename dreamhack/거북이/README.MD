


## 추가학습
### 디렉터리 생성
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
* parents=True 로 중간 디렉터리를 자동으로 생성할 수 있다. 즉, a/b/c/uploads를 만들 때 a,b,c 폴더가 없어도 모두 생성된다.
* exist_ok=True 를 지정하면 폴더가 이미 있어도 에러가 발생하지 않는다. 만약 False라면 이미 있는 경우 FileExistsError가 뜬다.

### JSON.stringfy vs res.json()
* JSON.stringfy는 Javscript 객체를 사람이 읽을 수 있는 문자열로 변환한다.
* res.json()은 서버 응답 파싱용으로 서버에서 온 JSON 문자열을 Javascript 객체로 변환한다.
* 참고로 flask에서 python 딕셔너리를 JSON 형태의 HTTP 응답으로 변환하는 jsonify 함수도 있다.

### ZIP Slip 취약점
* 압축 파일에 포함된 파일 경로명에 경로 조작(path traversal) 문자를 포함할 때 발생하는 보안 취약점이다.
* 공격자가 압축 파일 안에 ../와 같이 상위 디렉터리로 이동하는 경로를 포함한 파일명을 넣으면, 압축을 해제할 때 서버에서 임의의 위치에 파일을 쓰거나 덮어쓸 수 있게 된다.
* 압축을 해제하는 코드가 압축 파일 내부의 파일명을 검증하지 않고 그대로 사용하는 경우 발생한다.


## 문제 풀이
Step 1
* app.py의 /uploads의 코드를 보자. zip 파일을 파일명과 MIME 타입으로 감지하고, zip 파일에 대해 파일의 모든 바이너리 데이터를 메모리로 읽어온다. 그리고 ZipFile 객체를 생성한다.
    ```python
    if (f.filename or "").lower().endswith(".zip") or "zip" in (f.content_type or "").lower():
        data = f.read()
        zf = zipfile.ZipFile(io.BytesIO(data))
        names = []
        for info in zf.infolist():
            target = UPLOAD_DIR / info.filename
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            names.append(info.filename)
        return jsonify(ok=True, saved=names)
    ```
    * target = UPLOAD_DIR / info.filename 을 보면 zip 파일 안의 info.filename을 그대로 믿고 사용하는 것을 알 수 있다. path traversal 공격이 가능해보인다. 즉 info.filename이 "../templates/test.html"이면 templates/test.html이 덮어써지는 zip slip 취약점이 발생하는 것이다. 참고로 저러한 문법이 가능한 것은 app.py에서 from pathlib import Path의 pathlib 방식 때문이다.
    * zip 파일에서 폴더의 경우와 파일의 경우를 분리해서 처리한다. 파일은 파일을 저장하기 전에 상위 폴더부터 생성하는 것을 알 수 있다. 

* 일반 파일 업로드는 파일이름을 바꿔 저장하는 것을 알 수 있다.
    ```python
    ext = Path(f.filename).suffix.lower()
    file_name = f"{count}{ext}" if ext else f"{count}"
    count += 1
    out = UPLOAD_DIR / file_name
    out.parent.mkdir(parents=True, exist_ok=True)
    f.save(out)
    return jsonify(ok=True, saved=str(file_name))  
    ```

* app.py에서 정적 파일 제공 기능도 제공한다. 
    ```python
    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename):
        return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)
    ```
    * 위 코드는 flask의 동적 라우팅 문법으로 <path:filename>을 사용해 /를 포함한 전체 경로를 받을 수 있다.
    * send_from_directory(dicrectory, filename, options)에서 directory는 기준 디렉터리, filename은 요청된 파일 경로를 의미한다. 위 코드에서는 UPLOAD_DIR 기준으로 파일명을 통해 상대 경로를 지정한다. as_attachment=False이므로 브라우저에서 직접 표시하는 방식이다.
    * send_from_directory는 지정된 디렉터리 내에서만 파일을 찾아 보낸다. 따라서 기본적으로 상대 경로 탐색을 막는다. 이 경로는 단순히 업로드된 파일을 정적 파일로 전달하기 때문에, Jinja2 템플릿처럼 서버에서 동적으로 렌더링하지 않는다.


Step 2
/test.html로 접근하면 test.html을 Jinja2 템플릿이 랜더링하는 것을 이용하자. SSTI를 이용해 payload = "{{ config.__class__.__init__.__globals__['os'].popen('cat /flag').read() }}"로 test.html을 작성하면 된다. 파일명을 ../templates/test.html로 두고 압축한 exploit.zip을 파일 업로드하고, /test.html로 접속하면 SSTI로 입력한 페이로드가 실행되면서 플래그가 나온다.


## 시행착오
webshell.php를 올려봤다. 서버가 flask 애플리케이션이라 /uploads/webshell.php를 요청했을 때 php 실행 엔진을 거치지 않는 것으로 보인다.


## 결과
exploit.py에 exploit.zip을 만드는 코드를 작성했다. exploit.zip을 파일 업로드하고 /test.html로 접속하자.


