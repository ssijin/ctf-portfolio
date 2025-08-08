const home_url = "http://host8.dreamhack.games:20184/fish";

for (let i = 0; i < 23; i++) {
    let arr = Array(23).fill("0");
    arr[i] = "1";
    // 배열의 각 값을 "probs=값"의 형태의 문자열로 바꾸고 &으로 join한다.
    let data = arr.map(v => `probs=${v}`).join("&");

    fetch(home_url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: data
    })
    .then(r => r.text())
    .then(txt => {
        console.log(txt)
    });
}