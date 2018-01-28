import json


class AnimeFile(object):
    def __init__(self, anilist_id, filename, anime_name, season, episode, timeline, similarity, tokenthumb=None):
        self.anilist_id = anilist_id
        self.filename = filename
        self.anime_name = anime_name
        self.season = season
        self.episode = episode
        self.timeline = timeline
        self.similarity = similarity
        self.tokenthumb = tokenthumb

    def convert_to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False,
                          sort_keys=True, indent=4)
