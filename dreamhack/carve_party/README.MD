# Challenge: dreamhack - carve_party

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/96/

Tool : 개발자도구 사용

호박을 10000번 클릭하는 문제인데, 콘솔에서 pumpkin을 10000번 클릭하는 코드를 짜면 될듯하다.


## 문제 풀이
step 1
* make 함수
    * make 함수가 핵심으로, 클릭할 때마다 실행되는 것을 알 수 있다. 0~1000번 클릭할 때는 jack-nose의 opacity(불투명도)가 증가하는 등 횟수에 따라 점차 모습을 드러낸다.
    * counter, 즉 클릭 횟수가 10000을 넘으면 캔버스에 문자열을 출력한다. pumpkin 배열을 돌면서 String.fromCharcode(x)를 적용하고 join하므로 문자열을 생성하는 것을 알 수 있다.
    * 클릭 횟수가 10000 이하이면 남은 클릭 수를 표시하게끔 한다.
    ```javascript
    function make() {
    if (0 < counter && counter <= 1000) {
        $('#jack-nose').css('opacity', (counter) + '%');
    }
    else if (1000 < counter && counter <= 3000) {
        $('#jack-left').css('opacity', (counter - 1000) / 2 + '%');
    }
    else if (3000 < counter && counter <= 5000) {
        $('#jack-right').css('opacity', (counter - 3000) / 2 + '%');
    }
    else if (5000 < counter && counter <= 10000) {
        $('#jack-mouth').css('opacity', (counter - 5000) / 5 + '%');
    }

    if (10000 < counter) {
        $('#jack-target').addClass('tada');
        var ctx = document.querySelector("canvas").getContext("2d"),
        dashLen = 220, dashOffset = dashLen, speed = 20,
        txt = pumpkin.map(x=>String.fromCharCode(x)).join(''), x = 30, i = 0;

        ctx.font = "50px Comic Sans MS, cursive, TSCu_Comic, sans-serif"; 
        ctx.lineWidth = 5; ctx.lineJoin = "round"; ctx.globalAlpha = 2/3;
        ctx.strokeStyle = ctx.fillStyle = "#1f2f90";

        (function loop() {
        ctx.clearRect(x, 0, 60, 150);
        ctx.setLineDash([dashLen - dashOffset, dashOffset - speed]); // create a long dash mask
        dashOffset -= speed;                                         // reduce dash length
        ctx.strokeText(txt[i], x, 90);                               // stroke letter

        if (dashOffset > 0) requestAnimationFrame(loop);             // animate
        else {
            ctx.fillText(txt[i], x, 90);                               // fill final letter
            dashOffset = dashLen;                                      // prep next char
            x += ctx.measureText(txt[i++]).width + ctx.lineWidth * Math.random();
            ctx.setTransform(1, 0, 0, 1, 0, 3 * Math.random());        // random y-delta
            ctx.rotate(Math.random() * 0.005);                         // random rotation
            if (i < txt.length) requestAnimationFrame(loop);
        }
        })();
    }
    else {
        $('#clicks').text(10000 - counter);
    }
    }
    ```

* 이벤트 바인딩
    * #jack-target을 클릭했을 때에 대한 동작은 count를 증가시키고 100번 클릭할 때마다 pumpkin 배열 값을 xor을 통해 바꾼다. 따라서 단순히 counter를 바꾼다고 문제가 해결되지 않는다.
    ```javascript
    $(function() {
    $('#jack-target').click(function () {
        counter += 1;
        if (counter <= 10000 && counter % 100 == 0) {
            for (var i = 0; i < pumpkin.length; i++) {
                pumpkin[i] ^= pie;
                pie = ((pie ^ 0xff) + (i * 10)) & 0xff;
            }
        }
        make();
    });
    });
    ```

step 2

 * 그렇다면 로직을 알고 있으니 counter를 바꾸지 말고, 초기 pumpkin 배열을 counter에 따라 수정하는 코드를 만들면 되지 않나?
10000번 연산하는 자동화 코드 pumpkin.js를 콘솔에서 실행시키면 플래그가 나온다.
사실 아래와 같이 콘솔에서 jack-target을 10000번 클릭하는 코드를 돌려도 잘 나온다.

    ```javascript

    i=0;
    while(i<10001){
        $('#jack-target').click();
        i++;
    }
    ```



## 결과
호박을 10000번 클릭한 것과 같은 효과를 내면 플래그가 나온다.