from attr import dataclass
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


@dataclass
class ClientVolumeState:
    mute: bool
    volume_percent: int


class ClientVolumeControl:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self._audio_endpoint = interface.QueryInterface(IAudioEndpointVolume)
        self._range = self._audio_endpoint.GetVolumeRange()

    def set(self, state: ClientVolumeState):
        self._audio_endpoint.SetMute(state.mute, None)
        self._audio_endpoint.SetMasterVolumeLevelScalar(
            self._from_percent(state.volume_percent), None
        )

    def get(self) -> ClientVolumeState:
        return ClientVolumeState(
            mute=self._audio_endpoint.GetMute(),
            volume_percent=self._to_percent(
                self._audio_endpoint.GetMasterVolumeLevelScalar()
            ),
        )

    def _to_percent(self, volume: float):
        return 100 * (volume - self._range[0]) / (self._range[1] - self._range[0])

    def _from_percent(self, volume: int):
        return self._range[0] + (float(volume) / 100) * (
            self._range[1] - self._range[0]
        )
