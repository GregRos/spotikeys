from src.kb.triggered_command import FailedCommand, OkayCommand, TriggeredCommand
from src.spotify.now_playing import MediaStatus


MediaOkay = OkayCommand[MediaStatus]
MediaFailed = FailedCommand
MediaExecuted = MediaOkay | MediaFailed
MediaStageMessage = MediaExecuted | TriggeredCommand
