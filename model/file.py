class File(object):
    def __init__(self, file_id, name, size, mime_type, author, create_time):
        self.file_id = file_id
        self.name = name
        self.size = size
        self.mime_type = mime_type
        self.author = author
        self.create_time = create_time
