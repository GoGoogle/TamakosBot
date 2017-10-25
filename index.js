const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios')
const utils = require('./utils')
const util = require('util')

const token = '385193660:AAEakfWdmdEVwBsnCm6WogV7ZioLptpnRqI';
const bot = new TelegramBot(token, {
  polling: true
});

bot.on('message', (msg) => {

  if (msg.text.toLowerCase().indexOf('hi') === 0) {
    bot.sendMessage(msg.from.id, "Hi " + msg.from.first_name, {
      reply_to_message_id: msg.message_id
    })
  }

  if (msg.text.toLowerCase().includes('bye')) {
    bot.sendMessage(msg.from.id, "Hope to see you around again , Bye")
  }

});

bot.onText(/\/start/, (msg) => {

  bot.sendMessage(msg.from.id, "噫~");

});

bot.onText(/\/s (.+)/, (msg, match) => {
  const fromId = msg.from.id;
  const transText = match[1];
  const api = "http://translate.hotcn.top/translate/api"

  axios.post(api, { text: transText }).then((res) => {
    bot.sendMessage(fromId, res.data.text, { reply_to_message_id: msg.message_id });
  })
});

bot.onText(/\/wget (.+)/, (msg, match) => {

  const document_uri = match[1];
  const document_name = document_uri.substring(document_uri.lastIndexOf('/') + 1, document_uri.length)
  const re_options = { reply_to_message_id: msg.message_id }

  const chatId = msg.chat.id

  utils.downloadDocument(bot, chatId, document_uri, re_options, document_name)
});

bot.onText(/\/netease (.+)/, (msg, match) => {
  const chatId = msg.chat.id
  const music_name = match[1];

  // 遍历，生成候选项列表
  async function generateNewMusicArray(title_name) {
    let music_arr = []
    let array = await utils.getNeteaseMusicArray(title_name)
    array.forEach((v, i, a) => {
      music_arr.push([{
        text: '[' + (v.duration / 60000).toFixed(2) + ']' + v.name + '(' + v.artists[0].name + ')',
        callback_data: v.id + ':##:' + v.artists[0].name + ' - ' + v.name
      }])
    })
    return music_arr
  }

  // 展示歌曲列表
  async function selectMusicItem(title_name) {
    let res1 = await generateNewMusicArray(title_name)
    let res2 = await bot.sendMessage(chatId, "☁️关键字 " + title_name + " ", {
      reply_markup: {
        // 只展示最多前5个
        inline_keyboard: res1.slice(0, 5)
      },
      reply_to_message_id: msg.message_id
    })

    bot.on("callback_query", async function (q) {

      let url = await utils.getNeteaseMusicUrl(q.data.split(':##:')[0])

      // 必须使用国内的服务器下载
      utils.downloadAudio(bot, chatId, url, msg.message_id, q.data.split(':##:')[1] + '.mp3')
      // bot.sendMessage(chatId, url, { reply_to_message_id: msg.message_id });

      await bot.deleteMessage(res2.chat.id, res2.message_id)

    });
  }

  selectMusicItem(music_name)

})

