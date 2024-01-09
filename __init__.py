from os.path import join, dirname

from json_database import JsonStorage
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class WayneJuneLovecraftReadingsSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.AUDIOBOOK]
        self.default_image = f"{dirname(__file__)}/res/wayne_june.png"
        self.skill_icon = f"{dirname(__file__)}/res/icon.png"
        self.default_bg = f"{dirname(__file__)}/res/bg.jpeg"
        self.db = JsonStorage(f"{dirname(__file__)}/res/waynejune.json")
        super().__init__(*args, **kwargs)
        self.load_ocp_keyword_from_csv(f"{dirname(__file__)}/res/wayne_june.csv")

    @ocp_search()
    def ocp_waynejune_lovecraft_playlist(self, phrase):
        entities = self.ocp_voc_match(phrase)
        score = 25 if len(entities) else 0
        score += 30 * len(entities)
        yield {
            "match_confidence": score,
            "media_type": MediaType.AUDIOBOOK,
            "playlist": self.featured_media(),
            "playback": PlaybackType.AUDIO,
            "skill_icon": self.skill_icon,
            "image": self.default_bg,
            "bg_image": self.default_bg,
            "title": "Lovecraft - read by Wayne June (Compilation Playlist)",
            "author": "H. P. Lovecraft",
            "album": "read by Wayne June"
        }

    @ocp_search()
    def search(self, phrase, media_type):
        """Analyze phrase to see if it is a play-able phrase with this skill.

        Arguments:
            phrase (str): User phrase uttered after "Play", e.g. "some music"
            media_type (MediaType): requested CPSMatchType to media for

        Returns:
            search_results (list): list of dictionaries with result entries
            {
                "match_confidence": MatchConfidence.HIGH,
                "media_type":  CPSMatchType.MUSIC,
                "uri": "https://audioservice.or.gui.will.play.this",
                "playback": PlaybackType.VIDEO,
                "image": "http://optional.audioservice.jpg",
                "bg_image": "http://optional.audioservice.background.jpg"
            }
        """
        base_score = 15 if media_type == MediaType.AUDIOBOOK else 0
        entities = self.ocp_voc_match(phrase)
        book_name = entities.get("book_name")
        author = entities.get("book_author")
        base_score += 30 * len(entities)

        scores = {}
        for k in self.db:
            scores[k] = base_score
            if author:
                scores[k] += 30  # ensure min 50 score

        if book_name:
            scores[book_name] = base_score + 85

        for k, v in scores.items():
            if v >= 50 or author:
                yield {
                    "match_confidence": min(100, v),
                    "media_type": MediaType.AUDIOBOOK,
                    "uri": self.db[k]["uri"],
                    "playback": PlaybackType.AUDIO,
                    "image": join(dirname(__file__), self.db[k]["image"]),
                    "bg_image": self.default_bg,
                    "skill_icon": self.skill_icon,
                    "length": self.db[k]["length"],
                    "title": k,
                    "author": "H. P. Lovecraft",
                    "album": "read by Wayne June"
                }

    @ocp_featured_media()
    def featured_media(self):
        return [
            {"media_type": MediaType.AUDIOBOOK,
             "uri": entry["uri"],
             "playback": PlaybackType.AUDIO,
             "image": join(dirname(__file__), entry["image"]),
             "bg_image": self.default_bg,
             "skill_icon": self.skill_icon,
             "length": entry["length"],
             "title": title,
             "author": "H. P. Lovecraft",
             "album": "read by Wayne June"
             } for title, entry in self.db.items()
        ]


