# Challenge: dreamhack - File-download-1

## 문제 설명 & 접근
File Download 취약점이 존재하는 웹 서비스
flag.py를 다운로드 받으면 플래그를 획득할 수 있다고 한다.


## 문제 풀이
* app.py의 read() 부분을 보면 /read?name=파일명 으로 접속하면 서버가 uploads/파일명 을 열어 내용을 보여주는 것을 알 수 있다.
* upload() 쪽에는 상위 디렉터리로의 파일 업로드를 막아두었지만, read()에서는 별도의 코드가 없다.
* 바로 /read?name=flag.py를 입력하면 그런 파일은 없다고 출력된다.
* 따라서 url에서 파일명을 ../flag.py 로 접속을 시도해보자.

## 결과
/read?name=../flag.py 로 접속하면 flag가 나온다.

