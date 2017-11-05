def upload_file(bot, update):
    audio = update.message.audio
    video = update.message.video
    document = update.message.document
    if audio:
        print('audio:', audio.file_id)
    if video:
        print('video:', video.file_id)
    if document:
        print('document', document.file_id)
