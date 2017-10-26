const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios')
const tools = require('./tools')
const utl = require('util')

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

  const s_chat_id = msg.chat.id

  tools.downloadDocument(bot, s_chat_id, document_uri, re_options, document_name)
});





bot.onText(/\/netease (.+)/, async function (netease, netease_params) {

  // 生成搜索结果的 歌曲列表
  async function produceMusicPanel(music_name, music_curr_page) {
    // 搜索的 songs 结果
    const search_result = await tools.searchNeteaseMusicSongs(music_name, music_curr_page)

    // 搜索结果的总页数
    const music_total_page_num = search_result.songCount === 0 ? 0 : Math.ceil(search_result.songCount / 5)

    let music_arr = []

    if (music_total_page_num !== 0) {
      search_result.songs.forEach((v, i, a) => {
        music_arr.push([{
          text: '[' + (v.duration / 60000).toFixed(2) + ']' + v.name + '(' + v.artists[0].name + ')',
          callback_data: v.id
        }])
      })

      if (music_curr_page === 1) {
        music_arr.push([{
          text: '下一页',
          callback_data: 'next_action' + 'pageNum' + music_curr_page + 'keywords' + music_name
        }])
      } else if (music_curr_page < music_total_page_num) {
        music_arr.push([
          {
            text: '上一页',
            callback_data: 'previous_action' + 'pageNum' + music_curr_page + 'keywords' + music_name
          },
          {
            text: '下一页',
            callback_data: 'next_action' + 'pageNum' + music_curr_page + 'keywords' + music_name
          }
        ])
      } else if (music_curr_page === music_total_page_num) {
        music_arr.push([{
          text: '上一页',
          callback_data: 'previous_action' + 'pageNum' + music_curr_page + 'keywords' + music_name
        }])
      }

      music_arr.push([{
        text: '取消',
        callback_data: 'cancel_action'
      }])
    }

    return {
      content: music_arr,
      currPageNum: music_curr_page,
      totalPageNum: music_total_page_num
    }
  }


  async function sendPagePanel(keyword, currPageNum) {
    const panel = await produceMusicPanel(keyword, currPageNum)

    if (panel.totalPageNum === 0) {
      bot.sendMessage(netease.chat.id, "233，此歌曲未找到~", {
        reply_to_message_id: netease.message_id
      })
      return
    }

    await bot.sendMessage(netease.chat.id, utl.format("☁️🎵关键字 「%s」p: %s/%s",
      netease_params[1], panel.currPageNum, panel.totalPageNum), {
        reply_markup: {
          inline_keyboard: panel.content
        },
        reply_to_message_id: netease.message_id
      })
  }

  // 获取 关键词，当前页码。修改内容（由关键词和页码确定）、当前页码和总页码。
  async function modifyPagePanel(obj, isNext) {

    const keyword = obj.data.substring(obj.data.indexOf('keywords') + 8)
    let pageCode = parseInt(obj.data.substring(obj.data.indexOf('pageNum') + 7, obj.data.indexOf('keywords')))

    isNext ? pageCode += 1 : pageCode -= 1

    const newPanel = await produceMusicPanel(keyword, pageCode)

    const editOptions = {
      chat_id: obj.from.id,
      message_id: obj.message.message_id,
      reply_markup: {
        inline_keyboard: newPanel.content
      }
    }

    await bot.editMessageText(utl.format("☁️🎵关键字 「%s」p: %s/%s",
      keyword, newPanel.currPageNum, newPanel.totalPageNum), editOptions)

  }

  bot.removeAllListeners() // 移除未知的监听

  // 发送候选歌曲菜单
  sendPagePanel(netease_params[1], 1)

  // 监听回调查询语句
  bot.on("callback_query", async function (q) {
    if (q.data.startsWith('next_action')) {
      modifyPagePanel(q, true)
    }
    if (q.data.startsWith('previous_action')) {
      modifyPagePanel(q, false)
    }
    if (q.data === 'cancel_action') {
      await bot.deleteMessage(q.from.id, q.message.message_id)
    }
    if (!isNaN(q.data)) {
      let music_url_detail = await tools.getNeteaseMusicUrlDetail(q.data)
      let song_detail = await tools.getNeteaseMusicSongDetail(q.data)
      tools.downloadAudio(bot, q.from.id, music_url_detail.url, q.message.message_id, song_detail, music_url_detail)
    }
  });
}
)

