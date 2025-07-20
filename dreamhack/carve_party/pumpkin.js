var pumpkin = [124, 112, 59, 73, 167, 100, 105, 75, 59, 23, 16, 181, 165, 104, 43, 49, 118, 71, 112, 169, 43, 53];
var pie = 1;

for (let counter = 0; counter <= 10000; counter++) {
    if (counter % 100 === 0 && counter !== 0) {
        for (let i = 0; i < pumpkin.length; i++) {
            pumpkin[i] ^= pie;
            pie = ((pie ^ 0xff) + (i * 10)) & 0xff;
        }
    }
}

let result = pumpkin.map(x => String.fromCharCode(x)).join('');
console.log(result);
