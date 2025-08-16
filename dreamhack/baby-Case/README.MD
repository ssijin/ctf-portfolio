# Challenge: dreamhack - baby-Case

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1401


## 문제 풀이
step 1
* nginx.conf 설정 파일부터 보자. events 블록은 Nginx의 연결 처리 방식을 설정한다. 최대 1024개의 동시 연결을 지원한다. http 블록은 웹 서버 관련 모든 설정을 포함한다. location = /shop, /shop/일 때 모든 클라이언트의 접근을 거부하는 것을 알 수 있다. 즉, 403 forbidden 응답을 반환한다. 또한 루트 경로 이하 모든 요청에 대해 리버스 프록시를 설정해 들어온 요청을 app:3000 서버로 전달한다. 
    ```
    events {
        worker_connections  1024;
    }

    http {
        server {
            listen 80;
            listen [::]:80;
            server_name  _;
            
            location = /shop {
                deny all;
            }

            location = /shop/ {
                deny all;
            }

            location / {
                proxy_pass http://app:3000/;
            }

        }

    }
    ```
    * /shop에 일반적인 post로 접근이 불가하다. Express에서는 기본적으로 대소문자를 구분하지 않는다. 따따라서 /SHOP으로 접근해도 같은 핸들러로 처리된다.
    * leg=flag로 소문자로 Post body에 입력해 보내면 검증을 우회하면서 플래그를 얻을 수 있다.

## 결과
burp suite를 이용해 get 요청을 post 요청으로 변조하고 leg=flag를 설정하여 보내면 response로 플래그를 얻을 수 있다.