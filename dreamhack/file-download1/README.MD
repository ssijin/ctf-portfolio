# Challenge: dreamhack - File-download-1

## 문제 설명 & 접근
File Download 취약점이 존재하는 웹 서비스
flag.py를 다운로드 받으면 플래그를 획득할 수 있다고 한다.

## 추가 학습
* shutil 모듈의 rmtree()는 지정된 디렉터리와 그 안의 모든 파일과 서브 폴더를 재귀적으로 삭제한다. 따라서 아래와 같은 코드는 앱을 직접 실행할 때 기존 UPLOAD_DIR로 지정한 폴더가 있으면 완전히 지우고 새로 만든다. 서버 재시작될 때 자동 초기화해주는 기능을 한다.
    ```python
    if __name__ == "__main__":
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.mkdir(UPLOAD_DIR)
        APP.run(host="0.0.0.0", port=8000)
    ```
## 문제 풀이
* app.py의 read() 부분을 보면 /read?name=파일명 으로 접속하면 서버가 uploads/파일명 을 열어 내용을 보여주는 것을 알 수 있다.
* upload() 쪽에는 상위 디렉터리로의 파일 업로드를 막아두었지만, read()에서는 별도의 코드가 없다.
* 바로 /read?name=flag.py를 입력하면 그런 파일은 없다고 출력된다.
* /upload에서 ../flag.py를 입력하면 .. 필터링으로 인해 bad characters가 출력된다. read에서 .. 을 필터링하지 않는다는 것을 이용해 url에 /read?name=../flag.py 로 접속을 시도해보자.

* 추가 - 여기서는 왜 image-storage 문제에서 사용한 웹쉘이 업로드되어도 취약점으로 쓰이지 않는가? image-storage에서는 업로드된 php 파일(웹쉘)을 요청하면 웹서버가 php 해석기로 넘겨 실행이 되었다. 클라이언트가 실행 결과를 받으면서 웹쉘 명령이 동작한 것이다. 하지만 이 문제에서는 flask 서버에서 파일을 실행하는 것이 아니라 보통의 파일처럼 읽어서 화면에 그대로 출력하므로 php 웹쉘 스크립트가 실행되지 않는다.

## 결과
/read?name=../flag.py 로 접속하면 flag가 나온다.

