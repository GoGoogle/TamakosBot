const axios = require('axios')
const concat = require('concat-stream');
const request = require('request');

exports.downloadDocument = function (bot, chatId, document_uri, re_options, document_name) {
    async function getFile(buf, res1) {
        try {
            let res2 = await bot.editMessageText('正在下载~', {
                chat_id: chatId, message_id: res1.message_id
            })
            let res3 = await bot.sendDocument(chatId, buf, re_options, { filename: document_name })
            bot.deleteMessage(chatId, res2.message_id)
        } catch (err) {
            console.log(err)
            bot.sendMessage(chatId, 'There are some mistakes exist, please do not try again!')
        }
    }
    async function downloading() {
        let res1 = await bot.sendMessage(chatId, "获取中~", re_options)
        const concat_buf = concat((buf) => {
            getFile(buf, res1)
        })
        request(document_uri).pipe(concat_buf)
    }
    return downloading()
}

exports.downloadAudio = function (bot, chatId, audio_uri, msgId, audio_name, audio_duration) {
    async function getFile(buf, res1) {
        try {
            let res2 = await bot.editMessageText('正在下载~', {
                chat_id: chatId, message_id: res1.message_id
            })
            let res3 = await bot.sendAudio(chatId, buf, {
                reply_to_message_id: msgId,
                title: audio_name,
                duration: audio_duration
            })
            bot.deleteMessage(chatId, res2.message_id)
        } catch (err) {
            console.log(err)
            bot.sendMessage(chatId, 'There are some mistakes exist, please do not try again!')
        }
    }
    async function downloading() {
        let res1 = await bot.sendMessage(chatId, "获取中~", { reply_to_message_id: msgId })
        const concat_buf = concat((buf) => {
            getFile(buf, res1)
        })
        let options = {
            url: audio_uri
        }
        request(options).pipe(concat_buf)
    }
    return downloading()
}

exports.getNeteaseMusicUrl = async function (netease_music_id) {
    let res1 = await axios.get("/music/url", {
        params: {
            id: netease_music_id
        },
        proxy: {
            host: '127.0.0.1',
            port: 3000
        }
    })
    return res1.data.data[0].url
}

exports.getNeteaseMusicArray = async function (netease_music_name) {
    let res1 = await axios.get("/search", {
        params: {
            keywords: netease_music_name,
            limit: 30
        },
        proxy: {
            host: '127.0.0.1',
            port: 3000
        }
    })

    return res1.data.result.songs
}
