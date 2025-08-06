# Challenge: dreamhack - image-storage

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/38


## 추가 학습
* $_SERVER는 php에서 제공하는 superglobal array 중 하나로 웹 서버와 실행 환경에 대한 정보를 가지고 있다. $_SERVER['REQUEST_METHOD']로 HTTP 요청 방식의 정보를 얻을수도 있고 $_SERVER['REMOTE_ADDR']로 클라이언트의 IP 주소를 얻을 수도 있다.
* $_FILES는 php에서 자동으로 만들어주는 전역 배열이다. 클라이언트에서 enctype="multipart/form-data"로 파일 업로드 폼으로 보낸 파일 데이터가 이 배열에 저장된다. input_name은 HTML 폼 ```<input type="file" name="input_name">```에 지정한 name을 의미한다. 
    '''
    $_FILES = [
        'input_name' => [
            'name' => '파일원래이름',
            'type' => '파일종류(MIME type)',
            'tmp_name' => '서버에 임시로 저장된 파일 경로',
            'error' => 업로드 상태 코드,
            'size' => 파일 크기 (바이트)
        ],
        ...
    ];
    ```

## 문제 풀이
step 1
* upload.php 파일부터 뜯어보자. POST 요청을 받아, 사용자가 입력한 파일명이 업로드 경로에 있는지 검증하고 없다면, 서버 파일 시스템 내에서 임시 경로의 파일을 $directory 경로로 rename한다. 그 아래의 코드들은 입력폼에 대한 내용이다.
    ```php
    <?php
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        if (isset($_FILES)) {
        $directory = './uploads/';
        $file = $_FILES["file"];
        $error = $file["error"];
        $name = $file["name"];
        $tmp_name = $file["tmp_name"];
        
        if ( $error > 0 ) {
            echo "Error: " . $error . "<br>";
        }else {
            if (file_exists($directory . $name)) {
            echo $name . " already exists. ";
            }else {
            if(move_uploaded_file($tmp_name, $directory . $name)){
                echo "Stored in: " . $directory . $name;
            }
            }
        }
        }else {
            echo "Error !";
        }
    die();
    }
    ?>
    ```
* list.php에서는 scandir($directory)로 ./uploads/ 폴더 내 모든 파일명과 폴더명을 배열로 반환하고 여기서 array_diff로 두번째 인자의 요소들을 제외시킨다. array_diff는 두 개 이상의 배열을 비교해 첫 번째 배열에는 있고 나머지에는 없는 값을 반환하는 함수이다. 그리고 foreach로 하나씩 링크를 걸어 출력해준다.
    ```php
    <?php
        $directory = './uploads/';
        $scanned_directory = array_diff(scandir($directory), array('..', '.', 'index.html'));
        foreach ($scanned_directory as $key => $value) {
            echo "<li><a href='{$directory}{$value}'>".$value."</a></li><br/>";
        }
    ?> 
    ```
* 업로드 파일에 대한 검증이 없으므로 파일 업로드 취약점을 이용할 수 있다.

step 2
* 웹쉘을 구성하자. 파일은 webshell.php에 구성한다. 간단하게 사용자가 폼에 입력한 cmd를 os 명령어로 실행하는 파일이다. 이를 업로드하고 /list 에서 실행하면 웹쉘이 실행된다. 


## 결과
* 웹쉘을 실행시켜 나온 폼에 cat /flag.txt를 입력해 제출하면 플래그가 나온다.