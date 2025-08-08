# Challenge: dreamhack - ez_race

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/2058
키를 3초만에 찾으라는 문구가 있다.

## 추가 학습
* Flask에서 threaded=True 설정
    * threaded=False는 기본값으로 단일 thread를 의미한다. 즉, 한 번에 하나의 요청만 처리하며 동시 접근이 불가능하다. 따라서 Race Condition이 발생하지 않는다.
    * threaded=True는 여러 요청을 동시에 처리하기에 동시 접근이 가능하다. 따라서 Race Condition이 발생 가능하다.
* thread 사용
    * 아래코드처럼 target=try_value로 스레드가 실행할 함수를 지정하고, 함수에 전달한 인수를 넘길 수 있다. thread.start()로 스레드가 즉시 시작된다.
    ```python
    for i in range(1, 101):
        thread = threading.Thread(target=try_value, args=(i,))
        threads.append(thread)
        thread.start()  
    ```
## 문제 풀이
step 1
* app.py부터 뜯어보자. /flag에 접속할 때 전역변수 getflag가 1이면 플래그를 반환한다. 이에 대한 설정은 /race에 user 파라미터로 숫자를 받아 1부터 100까지의 랜덤숫자로 정해진 key와 일치하면 getflag가 1로 설정된다. 틀리면 time.sleep(3)으로 대기하고 새로운 키를 랜덤으로 생성한다.
* 서버 실행 부분을 보면 아래와 같이 멀티스레드가 활성화되어 있다. 따라서 여러 thread를 만들어 동시 접근 가능하다.
    ```python
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000, threaded=True)
    ```

step 2
* 따라서 여러 thread를 구성해 동시에 다른 user 파라미터를 넣어 요청하는 코드를 작성하자. 해당 코드는 bruteforce.py에 작성했다. 
* 예상 시나리오는 다음과 같다.
    스레드1: /race?user=50 → 틀림 → time.sleep(3) 시작
    스레드2: /race?user=30 → 틀림 → time.sleep(3) 시작
    스레드3: /race?user=42 → 맞음! → getflag = 1
    스레드4: /race?user=80 → 틀림 → time.sleep(3) 시작

    시간 3초 후:
    스레드1: key = random.randint(1, 100)  # 새 키 생성
    스레드2: key = random.randint(1, 100)  # 또 새 키 생성!
    스레드4: key = random.randint(1, 100)  # 또 새 키 생성!
* 

## 결과
* 스크립트를 실행하면 플래그가 나온다.