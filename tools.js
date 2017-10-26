const axios = require('axios')
const concat = require('concat-stream');
const request = require('request');
const utl = require('util')

exports.downloadDocument = function (bot, chatId, document_uri, re_options, document_name) {
    async function getFile(buf, res1) {
        try {
            let res2 = await bot.editMessageText('正在下载中....', {
                chat_id: chatId, message_id: res1.message_id
            })
            let res3 = await bot.sendDocument(chatId, buf, re_options, { filename: document_name })
        } catch (err) {
            console.log(err)
            bot.sendMessage(chatId, 'There are some mistakes exist, please do not try again!')
        } finally {
            bot.deleteMessage(chatId, res2.message_id)
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

exports.downloadAudio = function (bot, chatId, audio_uri, msgId, song_detail, music_url_detail, audio_duration) {
    const audio_name = utl.format('%s - %s', song_detail.ar[0].name, song_detail.name)
    async function getFile(buf, res1) {
        let res2
        try {
            res2 = await bot.editMessageText(utl.format('「%s」 正在下载中....', audio_name), {
                chat_id: chatId, message_id: res1.message_id
            })
            let res3 = await bot.sendAudio(chatId, buf, {
                reply_to_message_id: msgId,
                title: audio_name + '.mp3',
                disable_notification: false,
                duration: audio_duration,
                caption: utl.format("标题: %s\n艺术家: %s\n专辑: %s\n格式: %skbps\n☁️ID: %s",
                    song_detail.name,
                    song_detail.ar[0].name,
                    song_detail.al.name,
                    music_url_detail.type + ' ' + music_url_detail.br / 1000,
                    music_url_detail.id
                )

            })
        } catch (err) {
            bot.sendMessage(chatId, 'There are some mistakes exist, please do not try again!')
        } finally {
            bot.deleteMessage(chatId, res2.message_id)
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
        // !!!!!!!!!!!!! 必须使用国内的服务器下载 !!!!!!!!!!!!!!!!!!!!!!!!!
        request(options).pipe(concat_buf)
    }
    return downloading()
}

exports.getNeteaseMusicUrlDetail = async function (netease_music_id) {
    let res1 = await axios.get("/music/url", {
        params: {
            id: netease_music_id
        },
        proxy: {
            host: '127.0.0.1',
            port: 3000
        }
    })
    return res1.data.data[0]
}

exports.getNeteaseMusicSongDetail = async function (netease_music_id) {
    let res1 = await axios.get("/song/detail", {
        params: {
            ids: netease_music_id
        },
        proxy: {
            host: '127.0.0.1',
            port: 3000
        }
    })
    return res1.data.songs[0]
}

exports.searchNeteaseMusicSongs = async function (netease_music_name, music_curr_page) {
    let res1 = await axios.get("/search", {
        params: {
            keywords: netease_music_name,
            limit: 5,
            offset: music_curr_page * 5
        },
        proxy: {
            host: '127.0.0.1',
            port: 3000
        }
    })

    return res1.data.result
}
