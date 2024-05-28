from typeguard import check_type

from client.media.media_types import MediaStageMessage
from .desktop.desktop_hud import DestkopHUD
from .media.media_hud import MediaHUD
from src.ui import Component, Window, Ctx, Widget


class HUD(Component[Window]):
    def render(self, yld, ctx):
        if ctx.hidden == True:
            return
        if (
            check_type(ctx.executed, MediaStageMessage)
            and ctx.executed.command.group == "Media"
        ):
            yld(MediaHUD())
        else:
            yld(DestkopHUD())
