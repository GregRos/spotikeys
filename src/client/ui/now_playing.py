class MediaStatus:
    def __init__(
        self, title: str, artist: str, album: str, position: float, duration: float
    ):
        self.title = title
        self.artist = artist
        self.album = album
        self.position = position
        self.duration = duration

    @property
    def percent(self):
        return int(100 * self.position / self.duration)

    def __str__(self):
        return f"{self.artist} - {self.title} ({self.percent}%)"
