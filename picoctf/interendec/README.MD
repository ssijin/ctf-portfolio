# Challenge: picoCTF - interendec

## 문제 설명 & 접근
파일이 주어져있고 열었더니 다음과 같은 문자열이 있다.
YidkM0JxZGtwQlRYdHFhR3g2YUhsZmF6TnFlVGwzWVROclgyZzBOMm8yYXpZNWZRPT0nCg==

## 필요한 개념
#### Base64 인코딩
* Base64는 바이너리 데이터를 텍스트 기반 시스템에 포함시키기 위해 사용
* 3바이트(24비트)를 6비트로 나눈다. 6비트 값을 64(=2^6) 문자 중 하나로 매핑한다.


#### Base64 패딩
1. Base64는 항상 3바이트를 4개의 문자로 처리하므로 입력이 3바이트로 떨어지지 않는다면 부족한 부분을 채워야 한다.
2. Base64는 데이터를 맞추기 위한 패딩 문자로 =을 사용하며, 이는 인코딩 문자셋에는 포함되지 않는다.



## 문제 분석
주어진 문자열의 뒷부분이 ==으로 끝나는 걸 보면 Base64 인코딩된 것으로 의심된다.

## 문제 풀이
decode.py를 작성한다.
base64를 import하여 해당 문자열을 디코딩하여 출력하면 아래와 같이 또 패딩된 문자열이 나온다.
b'd3BqdkpBTXtqaGx6aHlfazNqeTl3YTNrX2g0N2o2azY5fQ=='

첫번째 디코딩 결과는 바이트 객체를 문자열로 표현한 것을 문자열 형태로 또 인코딩한 것으로 보인다.
따라서 strip으로 따옴표 안의 부분만 가져오고 다시 base64 디코딩을 진행한다.
wpjvJAM{jhlzhy_k3jy9wa3k_h47j6k69}

두번째 디코딩 결과는 잘 추출된 것으로 알 수 있고 특수기호 {}가 유지된 것을 caesar 암호화된 것으로 보인다.
for문을 돌리면서 picoCTF가 있는 문자열을 탐색한다.


## 결과
picoCTF{caesar_d3cr9pt3d_a47c6d69}
