# Challenge: dreamhack - Base64-based

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1785


## 추가 학습
### 전체 파일 경로 생성하는 방법
* __DIR__은 현재 스크립트가 위치한 디렉터리의 절대 경로를 나타낸다.
* DIRECTORY_SEPARATOR는 운영체제에 맞는 디렉터리 구분자를 제공한다.
* 여기에 파일명을 결합해 완전한 파일 경로를 만들 수 있다.

### php base64_decode() 함수 동작
base64_decode(string $data, bool $strict = false): string|false
* strict=false가 기본 동작으로, 공백 문자를 무시한다.
* strict=true일 때는 공백을 허용하지 않는다.

## 문제 풀이
step 1
* index.php를 뜯어보자.
    * 먼저 ALLOW_INCLUDE 상수를 true로 정의한다.
    * isset() 함수는 변수가 설정되어있고 null이 아닌지를 확인한다. $_GET['file']은 URL 쿼리 스트링에서 file 파라미터 값을 가져온다.
    * stripos() 함수는 대소문자를 구분하지 않고 문자열에서 특정 부분 문자열을 찾는다. 여기서 Li4v는 "../"를 base64로 인코딩한 값으로 해당 코드는 path traversal 공격을 막는다. 그 다음은 "flag"를 base64로 인코딩한 부분 문자열 "ZmxhZ" (decoding하면 fla가 나온다), "php"를 base로 인코딩한 부분 문자열 "aHA=" (decoding하면 hp가 나온다)를 차단한다.
    * 이후 base64_decode()로 인코딩된 문자열을 원래 형태로 디코딩한다.
    * realpath()는 심볼릭 링크나 상대 경로를 해석하여 실제 절대 경로를 반환하고 strpos(..., __DIR__)는 실제 파일 경로가 현재 디렉터리로 시작하는지를 확인한다. 이를 통해 path traversal로 현재 디렉터리 밖의 파일에 접근하는 것을 방지한다.
    * require_once()는 지정된 파일을 현재 스크립트에 포함시키고 실행한다. 이미 포함된 파일이라면 다시 포함하지 않는다.
    ```php
    <?php        
        define('ALLOW_INCLUDE', true);
        if (isset($_GET['file'])) {
            $encodedFileName = $_GET['file'];
            if (stripos($encodedFileName, "Li4v") !== false){
                echo "<p class='error'>Error: Not allowed ../.</p>";
                exit(0);
            }
            if ((stripos($encodedFileName, "ZmxhZ") !== false) || (stripos($encodedFileName, "aHA=") !== false)){
                echo "<p class='error'>Error: Not allowed flag.</p>";
                exit(0);
            }
            $decodedFileName = base64_decode($encodedFileName);

            $filePath = __DIR__ . DIRECTORY_SEPARATOR . $decodedFileName;

            if ($decodedFileName && file_exists($filePath) && strpos(realpath($filePath),__DIR__) == 0) {
                echo "<p>Including file: <strong>$decodedFileName</strong></p>";
                echo "<div>";
                require_once($decodedFileName);
                echo "</div>";
            } else {
                echo "<p class='error'>Error: Invalid file or file does not exist.</p>";
            }
        } else {
            echo "<p class='error'>No file parameter provided.</p>";
        }
        ?>
        ```
* flag.php를 base64 인코딩한 값인 ZmxhZy5waHA=에 대해 앞의 부분 문자열이 필터링되므로 공백을 추가해서 문자열을 구성하자. "Z m x h Z y 5 w a H A ="를 file의 value로 넘기면 필터링 우회 후 base64_decode에 의해 다시 합쳐지면서 flag.php가 된다.
* 또는 ./flag.php를 base64 인코딩하여 file의 value로 넘겨도 된다.


## 결과
* 위와 같이 index.php?file=value에 value를 잘 조정해주면 플래그를 얻을 수 있다.