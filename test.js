const axios = require('axios')

function searchNeteaseMusicSong() {
    var a = 3
    axios.get('/search', {
        params: {
            keywords: '明天你好',
            limit: 5,
            offset: 1 * 5
        },
        proxy: {
            host: '127.0.0.1',
            port: 3000
        }
    }).then((res) => {
        a = 4
        console.log(233) 
    })
    return a
}

console.log(searchNeteaseMusicSong())