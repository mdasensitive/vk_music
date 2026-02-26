# vk_audio.py
import requests
import time


class VKAudioError(Exception):
    pass

class TokenExpiredError(VKAudioError):
    """Токен истёк"""
    pass

class AccessDeniedError(VKAudioError):
    """Доступ запрещён"""
    pass

class RateLimitError(VKAudioError):
    """Превышен лимит запросов"""
    pass

class NotFoundError(VKAudioError):
    """Не найдено"""
    pass


class Track:
    def __init__(self, data):
        self.artist = data.get("artist", "")
        self.title = data.get("title", "")
        self.duration = data.get("duration", 0)
        self.url = data.get("url", "")
        self.is_available = bool(self.url)
        self.owner_id = data.get("owner_id")
        self.track_id = data.get("id")
    
    def __repr__(self):
        status = "✅" if self.is_available else "❌"
        return f"{status} {self.artist} — {self.title}"


class Playlist:
    def __init__(self, count, tracks):
        self.count = count
        self.tracks = tracks
    
    def __iter__(self):
        return iter(self.tracks)
    
    def __len__(self):
        return len(self.tracks)
    
    def __getitem__(self, index):
        return self.tracks[index]


class VKAudio:
    ERROR_CODES = {
        5: TokenExpiredError,
        6: RateLimitError,
        10: RateLimitError,  # Internal server error часто = rate limit
        15: AccessDeniedError,
        18: NotFoundError,
        29: RateLimitError,
        30: AccessDeniedError,
        43: AccessDeniedError,  # audio section unavailable
        201: AccessDeniedError,
    }
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            "User-Agent": "KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)"
        }
        self.base_url = "https://api.vk.com/method/"
        
        self.playlists = {
            "popular": {"owner_id": -147845620, "playlist_id": 2291},
            "new": {"owner_id": None, "playlist_id": None},
            "world_chart": {"owner_id": None, "playlist_id": None},
        }
    
    def _request(self, method, params):
        params["access_token"] = self.token
        params["v"] = "5.131"
        time.sleep(0.35)
        
        try:
            r = requests.get(self.base_url + method, params=params, headers=self.headers, timeout=10)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.Timeout:
            raise VKAudioError("Таймаут запроса")
        except requests.exceptions.ConnectionError:
            raise VKAudioError("Ошибка соединения")
        except requests.exceptions.RequestException as e:
            raise VKAudioError(f"Ошибка запроса: {e}")
        
        if "error" in data:
            error_code = data["error"].get("error_code", 0)
            error_msg = data["error"].get("error_msg", "Unknown error")
            
            error_class = self.ERROR_CODES.get(error_code, VKAudioError)
            raise error_class(f"[{error_code}] {error_msg}")
        
        return data
    
    def _parse_tracks(self, data):
        tracks = [Track(t) for t in data["response"]["items"]]
        return Playlist(data["response"]["count"], tracks)
    
    def get_popular(self, count=50):
        p = self.playlists["popular"]
        data = self._request("audio.get", {
            "owner_id": p["owner_id"],
            "playlist_id": p["playlist_id"],
            "count": count
        })
        return self._parse_tracks(data)
    
    def get_new(self, count=50):
        p = self.playlists["new"]
        if not p["owner_id"]:
            raise NotFoundError("Плейлист новинок не настроен")
        data = self._request("audio.get", {
            "owner_id": p["owner_id"],
            "playlist_id": p["playlist_id"],
            "count": count
        })
        return self._parse_tracks(data)
    
    def get_world_chart(self, count=50):
        p = self.playlists["world_chart"]
        if not p["owner_id"]:
            raise NotFoundError("Мировой чарт не настроен")
        data = self._request("audio.get", {
            "owner_id": p["owner_id"],
            "playlist_id": p["playlist_id"],
            "count": count
        })
        return self._parse_tracks(data)
    
    def get_user_music(self, user, count=50):
        if isinstance(user, str) and not user.isdigit():
            data = self._request("users.get", {"user_ids": user})
            user_id = data["response"][0]["id"]
        else:
            user_id = int(user)
        
        data = self._request("audio.get", {
            "owner_id": user_id,
            "count": count
        })
        return self._parse_tracks(data)
    
    def search(self, query, count=50):
        data = self._request("audio.search", {
            "q": query,
            "count": count,
            "sort": 2
        })
        return self._parse_tracks(data)
