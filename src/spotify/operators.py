import benedict


def get_artist(now_playing: benedict):
    x = now_playing.get('item.artists[0].id', None)
    return x


def get_album(now_playing: benedict):
    return now_playing.get('item.album.id', None)


def is_different_artists(now_playing1: benedict, now_playing2: benedict):
    return get_artist(now_playing1) != get_artist(now_playing2)


def is_different_albums(now_p1: benedict, now_p2: benedict):
    return get_album(now_p1) != get_album(now_p2)


def is_different_tracks(now_p1: benedict, now_p2: benedict):
    return get_track(now_p1) != get_track(now_p2)


def get_position(now_p: benedict):
    return now_p.get('progress_ms')


def get_track(now_p: benedict):
    return now_p.get('item.id', None)
