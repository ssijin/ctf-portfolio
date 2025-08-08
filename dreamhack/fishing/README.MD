# Challenge: dreamhack - Really Not SQL

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/2105
app.py와 index.html을 주어져있다.

search.js는 개발자 도구에 사용하는 자바스크립트 풀이 코드이다.

## 추가학습
* Flask 서버에서 python 리스트/딕셔너리를 템플릿으로 넘기기
    * 아래 코드는 서버의 fishes와 caught 데이터를 JSON 형식으로 변환해 자바스크립트 변수에 할당하는 코드이다.
    ```javascript
    const fishes = {{ fishes| tojson | safe }};
    let caught = {{ caught| tojson | safe }};
    ```
* 서버에서 보내는 JSON은 실제로 문자열이므로, 즉 서버가 {"name": "황금잉어"}이 데이터를 보내도 HTTP 응답에서는 '{"name": "황금잉어"}'처럼 따옴표로 감싸진 문자열로 잔달된다. 따라서 .json()으로 문자열을 자바스크립트에서 바로 쓸 수 있는 객체로 바꾸는 작업이 필요하다. 이 문제에서 서버에서 json 응답을 보낼 때는 jsonify로 파이썬 객체를 json 응답으로 바꿔주는 역할을 수행했다.
* 폼 데이터는 기본적으로 application/x-www-form-urlencoded 방식으로 전송된다. 예시로는 key1=value1&key2=value2&key2=value3 가 있다. 파이썬의 requests나 자바스크립트의 fetch에서 data="key1=value1&key2=value2&key2=value3"을 작성해 Content-Type: application/x-www-form-urlencoded으로 보내면 서버는 폼에서 입력받은 것과 똑같이 인식하게 된다.

## 문제 풀이
Step 1 
* app.py의 코드부터 확인해보자. 
    * 서버가 시작될 때 load_fishes()로 기본 물고기 정보를 생성한다.
    * /fish에 post를 보냈을 때 실행되는 코드를 보자. 사용자에게 probs 리스트를 받고 개수가 맞지 않으면 기본 확률값을 사용한다. 각 물고기에 대해 받은 확률값을 적용해 새로운 리스트 fishes를 만든다. pick_fish(fishes)로 랜덤한 한 마리를 뽑고 세션의 caught 리스트에 추가한다. 

* index.html의 스크립트 부분을 보자. 
    * 서버의 데이터를 받아서 등급별로 물고기를 분류한 객체를 생성한다.
    ```
    fishesByGrade = {
    "전설": [전설 물고기들...],
    "희귀": [희귀 물고기들...],
    "일반": [일반 물고기들...]
    }
    ```
    * showFishModal은 모달 창에 물고기 정보를 보여주는 함수이다. 물고기 이름이 "flag"이면 이미지 경로를 /flag_img로 처리하고 그 외로는 /static/물고기이미지파일명 경로로 설정한다. 
    * renderDex는 낚시 도감을 동적으로 구성한다. 등급별로 물고기를 표시하고 잡은 물고기는 이미지와 이름을 표시하고 못잡은 물고기는 unknown.png를 올리는 코드이다.

    * pullBtn 버튼을 누르면 /fish 엔드포인트에 post 요청을 보낸다
    ```javascript
    pullBtn.onclick = () => {
        if (missTimeout) clearTimeout(missTimeout);
        pullBtn.disabled = true;
        statusDiv.textContent = "낚싯대를 당기는 중...";
        fetch("/fish", { method: "POST" })
            .then(r => r.json())
            .then(data => {
                statusDiv.textContent = `축하합니다! (${data.grade}) ${data.name}를 잡았습니다!`;
                if (data.name === "flag") {
                    fishImg.src = "/flag_image";
                } else {
                    fishImg.src = "/static/" + encodeURIComponent(data.img);
                }
                fishImg.style.display = "";
                startBtn.disabled = false;
                if (!caught.includes(data.name)) {
                    caught.push(data.name);
                    renderDex();
                }
            });
        };
        ```


Step2
* /flag에 "probs=0&probs=1&probs=0&..." 같은 쿼리 문자열을 content-type을 application/x-www-form-urlencoded로 지정해 post하면 서버는 이 데이터를 폼 데이터로 인식한다. flask 서버에서 probs=[0.0, 1.0, 0.0, ...]의 형식으로 처리되는 것이다. 
* /flag의 로직에서 probs 리스트로 각 물고기의 확률값을 갱신하는 것을 알 수 있다. 즉, 위 쿼리 문자열을 조작해서 나머지 확률은 0, flag의 확률은 1로 조정하면 flag 물고기가 뽑히면서 caught에 flag가 추가되고 flag.jpg를 확인할 수 있게 된다.
* 이미지를 즉각적으로 확인하고자 개발자 도구에서 실행가능하도록 자바스크립트로 코드를 구성했다. 코드는 search.js에 있다. 코드를 개발자 도구 콘솔 창에서 실행하면 flag가 fishes의 가장 마지막 인덱스에 있다는 것도 확인할 수 있고 옆 modal에 flag.jpg가 나온다.
* 결과적으로 이 취약점은 사용자가 직접 폼 데이터를 조작해 서버에 원하는 확률값을 보낼 수 있다는 것이다. 서버가 사용자가 보낸 probs 리스트를 그대로 사용하기 때문에 flag 확률만 1로 설정하면 무조건 flag에 대한 정보를 얻을 수 있다.

## 결과
flag.jpg의 내용을 잘 입력하면 해결