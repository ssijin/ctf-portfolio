# Challenge: picoCTF - Hashcrack

## 문제 설명 & 접근
A company stored a secret message on a server which got breached due to the admin using weakly hashed passwords. Can you gain access to the secret stored within the server?
Access the server using nc verbal-sleep.picoctf.net 62644
* 접속하니, We have identified a hash: 482c811da5d5b4bc6d497ffa98491e38
* Enter the password for identified hash:
* 일단 hash가 16진수 128비트를 쓰고 있음 -> MD5 의심 

## 필요한 개념
#### MD5(Message Digest Algorithm 5)
1. MD5 processes a variable length message into a fixed-length output of 128 bits. 어떤 길이 메시지를 넣어도 128비트의 고정 길이 출력
2. The input message is broken up into chunks of 512-bit blocks; the message is padded so that its length is divisible by 512. (입력 메시지를 512비트 블록 단위로 나누고 메시지 길이가 512로 나누어떨어지게끔 패딩도 한다)
3. The remaining bits are filled up with a 64-bit integer representing the length of the original message. (남은 공간(비트)는 원래 메시지 길이를 나타내는 64비트 정수로 채운다)
4. The main MD5 algorithm operates on a 128-bit state, divided into four 32-bit words, denoted *A*, *B*, *C* and *D*.
5. These are initialized to certain fixed constants.(A, B, C, D는 항상 정해진 초기값으로 시작)
6. The main algorithm then operates on each 512-bit message block in turn, each block modifying the state. (각 블록은 chain 구조로 A, B, C, D를 업데이트하며 다음 블록에 영향을 준다)
7. The processing of a message block consists of four similar stages, termed *rounds*; each round is composed of 16 similar operations based on a non-linear function *F*, modular addition, and left rotation.(4라운드에 16스텝 ⇒ 64스텝 연산)
#### SHA1
1. SHA-1에서 메시지를 어떻게 Digest(160-bit 해시 값)로 변환하는지를 나타내는 구조
2. SHA-1은 입력을 512비트 블록 단위로 처리하며, 최종적으로 160비트 해시값을 출력한다.
3. Padding 및 메시지 준비 단계
* 원래 입력 메시지는 K비트일 수 있다. Padding은 1비트 하나와 0으로 채워 메시지의 총 길이가 512비트의 배수가 되도록 한다.
* L(예비 블록 개수) X 512 bits = N X 32 bits. 여기서 32bit는 뭐지? SHA-1는 각 블록에서 내부적으로 80개의 연산 라운드를 통해 압축된다. 이를 위해 각 블록은 16개의 32비트 워드로 분할된다.
* K mod 2^64는 SHA-1은 최대 2^64비트까지 메시지를 지원하므로 K가 그것보다 크면 나머지만 저장한다는 의미이다.
4. Block-by-Block 해시 처리 단계 (하단)
* 패딩된 메시지는 512비트 단위로 나누며 블록은 총 L개가 된다.
* IV는 Initial value로, SHA-1은 항상 고정된 초기값(IV)로 시작한다. (CV0)
* 각 $Y_i$ 블록은 이전 해시 결과($CV_{i-1}$)와 함께 SHA 컴프렌션 함수에 입력된다.
* 최종 출력으로 160비트 메시지 다이제스트가 생성된다.
5.$Y_q$는 현재 처리 중인 512비트 메시지 블록이며, $CV_q$는 이전 압축 결과(160비트 chaining value)로 32비트씩 A, B, C, D, E로 나뉘어 들어간다.
6. 512비트 메시지 블록 $Y_q$는 32비트씩 16개 워드로 나뉜다. 실제 조각은 (W[0], …, W[15]) 그리고 내부적으로 계산해서 $W_{16}$부터 $W_{80}$까지 확장한다.
7. SHA-1은 80번의 라운드로 동작하고 각 20라운드는 서로 다른 함수의 상수를 사용한다.


## 문제 풀이
분석할 내용이 없다.
1.hash가 주어졌으니, 비밀번호를 알아내보자. Hashes.com에 482c811da5d5b4bc6d497ffa98491e38를 입력하면 MD5일 가능성이 높으며 해당 도구를 더 써보면 password123인 것을 알 수 있다.

    ```
    We have identified a hash: 482c811da5d5b4bc6d497ffa98491e38
    Enter the password for identified hash: password123
    Correct! You've cracked the MD5 hash with no secret found!
    ```

2.입력했는데, 문제가 더 나온다.. 마찬가지로 Hashes.com에 b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3를 입력하면 Sha1일 가능성이 높으며 도구를 더 써보면 letmein인 것을 알 수 있다.

    ```
    Flag is yet to be revealed!! Crack this hash: b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3
    Enter the password for the identified hash: letmein
    Correct! You've cracked the SHA-1 hash with no secret found!
    ```

3.또 있다... 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745를 입력하면 SHA-256일 가능성이 높으며 qwerty098이 나온다.

    ```
    Almost there!! Crack this hash: 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745
    Enter the password for the identified hash: qwerty098
    Correct! You've cracked the SHA-256 hash with a secret found. 
    ```



## 결과
picoCTF{UseStr0nG_h@shEs_&PaSswDs!_3eb19d03}
