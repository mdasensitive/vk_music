# VK Audio

Модуль для работы с музыкой VK через Python.

## Что нужно

- Python 3.7+
- `pip install requests`
- Токен от Kate Mobile (обычный токен VK не катит, audio API закрыт с 2016)

## Как получить токен

Самый простой способ — через HTTP Canary на телефоне:

1. Ставишь Kate Mobile, логинишься
2. Ставишь HTTP Canary, включаешь захват
3. В Kate Mobile заходишь в музыку
4. В HTTP Canary ищешь запрос к `api.vk.com` — там будет `access_token`

Токен живёт долго, но может слететь если VK что-то заподозрит.

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

Ссылки на mp3 рабочие, можно качать. Но они временные — живут около суток.

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
    tracks = vk.get_user_music("кто-то")
except TokenExpiredError:
    print("токен сдох, нужен новый")
except AccessDeniedError:
    print("музыка закрыта у юзера")
except RateLimitError:
    print("слишком часто долбишь, подожди")
```

## Нюансы

- Между запросами стоит задержка 0.35 сек чтоб VK не банил
- Некоторые треки заблочены — у них `url` пустой и `is_available = False`
- Если ловишь error 10 — это VK тупит, просто повтори через пару секунд
