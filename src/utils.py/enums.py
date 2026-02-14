from enum import Enum


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    ARTIST_MANAGER = "artist_manager"
    ARTIST = "artist"


class Gender(str, Enum):
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"


class Genre(str, Enum):
    RNB = "rnb"
    COUNTRY = "country"
    CLASSIC = "classic"
    ROCK = "rock"
    JAZZ = "jazz"
