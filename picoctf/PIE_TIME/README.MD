# Challenge: picoCTF - PIE_TIME

## 문제 설명 & 접근
들어가니 프로그램의 소스 코드와 바이너리 파일을 준다.
그리고 아래와 같이 원격 접속할 수 있게끔 해준다.
Connect to the program with netcat:
$ nc rescued-float.picoctf.net XXXXX
원격 접속하니 main의 주소를 준다. 소스코드부터 분석해보자.

## 필요한 개념
#### PIE(Position-Independent Executable)
1. PIE는 프로그램이 실행될 때 항상 같은 주소에 로드되지 않도록 하는 보안 기능
2. PIE가 설정되어있으면 실행할 때마다 메모리에서 주소가 바뀐다.
3. 왜? 주소가 고정되어 있으면 익스플로잇 가능하니까

#### 함수 포인터
1. 함수도 메모리 어딘가에 저장되므로 주소를 가지고 있다. 함수 포인터는 함수 주소를 저장하고 나중에 그 주소로 점프하여 함수처럼 실행가능하다.
2. 필요한 이유 : 콜백 함수(동작을 외부 함수로 전달하고 실행), 여러 함수 중 하나를 선택적 실행, 주소를 직접 지정하여 코드 흐름 제어
3. void (*fp)(int);는 int를 인자로 받아 void를 반환하는 함수 포인터

#### SIGSEGV
1. SIGSEGV는 Segmentation fault를 뜻하는 시그널이다.
2. Segmentation fault : 프로그램이 접근해서는 안되는 메모리 영역에 접근했을 때 발생하는 오류

## 문제 분석
1.segment fault에 대한 핸들러
```python
void segfault_handler() {
    printf("Segfault Occurred, incorrect address.\n");
    exit(0);
}
```
2.win() 함수
```python
int win() {
  FILE *fptr;
  char c;

  printf("You won!\n");
  # Open file
  fptr = fopen("flag.txt", "r");
  if (fptr == NULL)
  {
      printf("Cannot open file.\n");
      exit(0);
  }

  # Read contents from file
  c = fgetc(fptr);
  while (c != EOF)
  {
      printf ("%c", c);
      c = fgetc(fptr);
  }

  printf("\n");
  fclose(fptr);
}
```
3.main함수
```python
int main() {
    # segmentation fault가 발생하면 segfault_handler를 실행
    signal(SIGSEGV, segfault_handler);
    # stdout의 버퍼렁을 제거해서 printf() 결과가 즉시 출력되게 한다.
    # printf()는 기본적으로 line buffered => 개행 나오기 전까지 출력이 지연될 수 있다
    setvbuf(stdout, NULL, _IONBF, 0); // _IONBF = Unbuffered

    printf("Address of main: %p\n", &main);

    unsigned long val;
    printf("Enter the address to jump to, ex => 0x12345: ");
    # 주소를 16진수 주소로 받는다.
    scanf("%lx", &val);
    printf("Your input: %lx\n", val);

    # function pointer. 입력받은 val을 함수 포인터로 캐스팅
    void (*foo)(void) = (void (*)())val;
    # 해당 주소로 call 시도, 입력값이 잘못된 주소면 CPU가 해당 주소에서 코드 실행 못하므로 SIGSEGV 발생
    foo();
}
```
4.scanf에 무엇을 넣어야하는가?
* 소스 코드를 보니 win과 main이 둘 다 하나의 c 파일 안에 들어가 있다. 컴파일하면 하나의 실행 파일로 묶이니, 동일한 바이너리 내의 고정된 상대 위치에 존재한다.
* 즉, PIE로 주소가 바뀌어도 main과 win 사이의 간격은 항상 같다.

5.그렇다면, 문제를 풀이하려면 받은 바이너리 파일에서 main과 win 사이의 offset을 알아내고, 원격 서버에 접근해서 얻은 main함수에 offset을 더해 win의 주소를 입력해야 한다.

## ✅ 풀이
0.offset (win 주소 - main 주소) 찾기


1.원격서버 접근
* $ nc rescued-float.picoctf.net 62893 에 접속

2.바이너리 파일의 보안속성 확인
* 아래 명령어를 입력하면 Mach-O 바이너리 보안 속성을 확인할 수 있다.
    ```bash
    otool -hv vuln
    ```
* flags 필드에 NOUNDEFS DYLDLINK TWOLEVEL PIE 적혀있다.
    * NOUNDEFS : 바이너리에 정의되지 않은 외부 심볼이 없다
    * DYLDLINK : 런타임에 Dynamic Linker와 링크
    * TWOLEVEL : 2레벨 심볼 바인딩 사용
    * PIE : PIE 적용됨

3.offset 구하기 (실패)
    ```bash
    nm vuln | grep 'T'
    ```
* nm 명령어는 ELF 또는 Mach-O 실행 파일에서 Symbol table을 보여주는 도구
* T는 텍스트 섹션에 있는 전역 함수 (즉, 실행 가능한 코드)를 의미한다.
* 실행 가능한 함수 중 전역으로 export되어 있는 것을 가져오라는 명령어
* 실행하면 아래와 같이 나온다.
    ```
    0000000100000000 T __mh_execute_header
    0000000100003dec T _main
    0000000100003d08 T _segfault_handler
    0000000100003d24 T _win
    ```
* offset은 0xC8
* 그런데 답이 나오지 않는다. 뭐지??
* file vuln 입력하면 vuln: Mach-O 64-bit executable arm64라고 뜨는 걸 봐서는 Mach-O 파일이 맞는데. 혹시 리눅스 환경에서 풀어야 하나? 근데 다운로드 받은 바이너리 파일이 ELF가 아닌데??
* UTM으로 우분투에서 공유 폴더에 집어넣어서 돌려보니 역시나 MACH-O라 nm이나 gdb를 못쓴다. 진짜 뭐지?

4.offset구하기 (성공)
* 우분투에서 picoctf를 접속해서 바이너리 파일을 받아보자. 그 파일이 ELF로 받아지면 offset 차이는 있겠지. 아니 그러면 서버코드단도 처리해줘야 하지 않나?
* 일단 gdb로 돌려보니 역시나 offset 값은 다르다. 구해보면 0x96
    ```
    During startup program exited with code 126.
    (gdb) p &main
    $1 = (<text variable, no debug info> *) 0x133d <main>
    (gdb) p &win
    $2 = (<text variable, no debug info> *) 0x12a7 <win>
    (gdb) quit

    ```
* 어차피 정적 바이너리 파일이라 nm이든 gdb든 리눅스 환경에서는 offset이 똑같다. nm은 PIE 환경에서 상대 절대 주소를 알 수 없고, gdb는 PIE 환경에서  start 후 실제 주소를 알 수 있다. 이 문제는 정적 바이너리로 offset만 알아내고 문제에서 main의 주소를 던져주므로 해당 offset에만 더해주면 된다.

5.offset값(0x96 더해서 입력)

## 결과
picoCTF{b4s1c_p051t10n_1nd3p3nd3nc3_80c3b8b7}

