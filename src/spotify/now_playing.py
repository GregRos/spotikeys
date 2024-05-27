from dataclasses import dataclass
from client.volume import VolumeInfo
from src.spotify.device import Device


@dataclass
class MediaStatus:
    artist: str
    title: str
    duration: float
    position: float
    is_playing: bool
    album: str
    volume: VolumeInfo
    device: Device

    @property
    def progress(self):
        return round(100 * self.position / self.duration)

    def __str__(self):
        return f"{self.artist} - {self.title} ({self.progress}%)"
