import base64


def caesar_decrypt(encoded, shift):
    result = ""
    for char in encoded:
        if "a" <= char <= "z":
            result += chr((ord(char) - ord("a") - shift) % 26 + ord("a"))
        elif "A" <= char <= "Z":
            result += chr((ord(char) - ord("A") - shift) % 26 + ord("A"))
        else:
            result += char
    return result


# 주어진 문자열
encoded = "YidkM0JxZGtwQlRYdHFhR3g2YUhsZmF6TnFlVGwzWVROclgyZzBOMm8yYXpZNWZRPT0nCg=="

# 1차 디코딩
decoded = base64.b64decode(encoded).decode("utf-8")

# strip & 2차 디코딩
real_base64 = decoded.strip()[2:-1]
decoded2 = base64.b64decode(real_base64).decode("utf-8")

for shift in range(26):
    decrypted = caesar_decrypt(decoded2, shift)
    if "picoCTF" in decrypted:
        print(decrypted)
