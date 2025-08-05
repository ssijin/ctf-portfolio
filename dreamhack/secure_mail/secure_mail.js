alert = function() {};

for(var yy=99;yy>=1;yy--){
    for(var mm=1;mm<=12;mm++){
      for(var dd=1;dd<=31;dd++){
        if(_0x9a220(yy * 10000 + mm * 100 + dd)) {
          console.log(yy * 10000 + mm * 100 + dd);
          return;
        }
      }
    }
}