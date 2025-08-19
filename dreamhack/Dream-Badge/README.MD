# Challenge: dreamhack - Dream Badge 

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1583/



## 문제 풀이
* 로그인 기능으로 삽질을 하다 dockerfile 언인텐 풀이로 풀게 되었다. dockerfile을 보자. Dockerfile에 flag가 정적으로 나와있는 것을 볼 수 있다. 그리고 /Dockerfile로 접근하면 플래그를 바로 얻을 수 있다.
    ```dockerfile
    # PHP 8.1 버전이 설치된 Apache의 웹 서버 환경을 제공
    FROM php:8.1-apache

    # libsqlite3-dev 설치, PHP 확장 모듈 pdo와 pdo_sqlite를 빌드/설치
    RUN apt-get update && apt-get install -y \
        libsqlite3-dev \
        && docker-php-ext-install pdo pdo_sqlite

    # /db 디렉터리 만들고, 모든 사용자에게 읽기/쓰기/실행 권한 부여  
    RUN mkdir -p /db && chmod -R 777 /db

    # 작업 디렉터리를 Apache의 웹 루트로 설정
    WORKDIR /var/www/html

    # 현재 빌드 컨텍스트의 모든 파일을 /var/www/html로 복사
    COPY . .

    RUN echo 'DH{sample_flag}' > /flag

    EXPOSE 80

    CMD ["apache2-foreground"]
    ```