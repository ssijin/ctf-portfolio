# Challenge: picoCTF - Even RSA can be broken??

## 문제 설명 & 접근
N과 e가 주어지고 cypertext가 주어진다.
N과 e만으로 cypertext를 해석할 수 있는지가 문제이며, 잘못된 파라미터 선택으로 생기는 취약점 문제로 보인다.

## 필요한 개념
#### RSA 키 생성 예제
1. 두 개의 소수 p, q 선택
2. N = p X q
3. 오일러함수 $\phi(N)=(p-1)(q-1)$
4. 공개지수 e 선택 (1<e<$\phi(N)$), $gcd(e, \phi(N))=1$
5. 개인지수 d 계산 ($d \equiv e^{-1} \pmod {\phi(N)} $)
6. 공개키는 (N,e), 개인키는 (d, p, q)  
#### RSA 암호화/복호화
1. $c \equiv m^e \pmod N$
2. $m \equiv c^d \pmod N$


## 문제 분석

이상하게 N이 짝수이다. N은 두 소수의 곱인데 짝수라는 것은 p나 q 둘 중 하나가 2라는 것이다!
p=2, q=N/2
따라서 $\phi(N)$도 구하기 쉽다. 이를 통해 역원인 d를 구해내면 복호화 가능하다.

## 문제 풀이
decrypt.py를 작성하자.
p와 q를 통해 3 argument를 사용하는 pow 함수를 통해 m을 도출한다.




## 결과
picoCTF{tw0_1$_pr!m3625a858b}
