# VK Audio

Модуль для работы с музыкой VK через Python.

- Python 3.7+

## Как юзать

```python
from vk_audio import VKAudio

vk = VKAudio("твой_токен")

# популярное
tracks = vk.get_popular(10)

# поиск
tracks = vk.search("SALUKI", 20)

# музыка юзера (по нику или id)
tracks = vk.get_user_music("zaremikkik", 50)
```

## Что получаешь

```python
for track in tracks:
    print(track.artist)      # исполнитель
    print(track.title)       # название
    print(track.url)         # прямая ссылка на mp3
    print(track.duration)    # длина в секундах
    print(track.is_available)  # доступен ли трек
```

Ссылки на mp3 рабочие, можно качать. Но они временные — живут около суток. (???)

## Методы

- `get_popular(count)` — популярное
- `get_new(count)` — новинки (нужно указать плейлист в коде)
- `get_world_chart(count)` — мировой чарт (тоже нужно указать)
- `get_user_music(user, count)` — музыка пользователя
- `search(query, count)` — поиск

## Ошибки

```python
from vk_audio import VKAudio, TokenExpiredError, AccessDeniedError, RateLimitError

try:
    tracks = vk.get_user_music("кто-то id или ник")
except TokenExpiredError:
    print("токен умер, нужен новый")
except AccessDeniedError:
    print("музыка закрыта у юзера")
except RateLimitError:
    print("слишком часто долбишь, подожди")
```

## Нюансы

- Между запросами стоит задержка 0.35 сек
- Некоторые треки заблочены — у них `url` пустой и `is_available = False`
