from dataclasses import dataclass
from typing import Any
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize


@dataclass
class ClientVolumeState:
    mute: bool
    volume_percent: int


@dataclass
class VolumeInfo:
    volume: int
    mute: bool


class ClientVolumeControl:
    _devices: list
    audio_interface: IAudioEndpointVolume | None = None

    def __init__(self):
        pass

    @property
    def audio_endpoint(self) -> Any:
        if self.audio_interface:
            return self.audio_interface
        try:
            devices = AudioUtilities.GetAllDevices()
        except OSError:
            CoInitialize()
            devices = AudioUtilities.GetAllDevices()
        device = [device for device in devices if device.state.name == "Active"][0]

        interface = device.EndpointVolume
        self.audio_interface = audio_interface = interface.QueryInterface(
            IAudioEndpointVolume
        )
        return audio_interface

    @property
    def info(self) -> VolumeInfo:
        return VolumeInfo(self.volume, self.mute)

    def _to_percent(self, volume: float):
        return int(volume * 100)

    def _from_percent(self, volume: int):
        return volume / 100

    @property
    def mute(self) -> bool:
        return self.audio_endpoint.GetMute()

    @mute.setter
    def mute(self, mute: bool):
        self.audio_endpoint.SetMute(mute, None)

    @property
    def volume(self) -> int:
        return self._to_percent(self.audio_endpoint.GetMasterVolumeLevelScalar())

    @volume.setter
    def volume(self, volume: int):
        volume = max(0, min(volume, 100))
        volume_float = self._from_percent(volume)
        self.audio_endpoint.SetMasterVolumeLevelScalar(volume_float, None)
