# Biblioman плъгин за Calibre

`biblioman-calibre` е плъгин за Calibre, който изтегля метаданни и корици от `https://biblioman.chitanka.info`.

С него Calibre може да намира структурирани данни за книги от Biblioman, каталога за книги на Читанка. Плъгинът използва публичните JSON адреси на Biblioman, а не HTML страниците, което прави търсенето по-стабилно и по-лесно за поддръжка.

## Изтегляне

- Latest release: `https://github.com/EdinUser/biblioman-calibre/releases/latest`

Страницата с latest release води до последното издание на проекта в GitHub. Самият zip файл на плъгина е в секцията с файловете към това издание.

## Какво прави плъгинът

- търси в Biblioman по Biblioman ID, ISBN, заглавие или заглавие плюс първи автор
- попълва заглавие, автори, издател, година на издаване, ISBN, анотация, тагове и поредица
- изтегля корици от Biblioman
- записва допълнителен идентификатор `biblioman` в Calibre

## Какви данни попълва

В момента плъгинът подава към Calibre следните полета:

- title
- authors
- publisher
- publication year като `pubdate`
- ISBN
- comments от анотацията
- tags от жанр, теми и категория
- series или sequence
- cover image
- допълнителен идентификатор `biblioman`

## Източник на данните

Плъгинът използва публичните JSON адреси на Biblioman:

- `GET /books/{id}.json`
- `GET /books.json?q=...`

Това хранилище е полезно, ако търсите:

- Calibre plugin for Bulgarian books
- Biblioman metadata source plugin
- Chitanka Biblioman cover download plugin
- Python пример за Calibre metadata source plugin

## Структура на проекта

- `plugin-src/__init__.py` - изходният код на плъгина
- `build-plugin.sh` - прави готовия zip файл за инсталиране
- `dist/` - генерирани build файлове, които не се commit-ват

## Build

```bash
./build-plugin.sh
```

Резултатът е:

```text
dist/BibliomanMetadata-0.1.0.zip
```

## Инсталиране в Calibre

1. Отворете `Preferences`.
2. Отворете `Plugins`.
3. Изберете `Load plugin from file`.
4. Отворете `https://github.com/EdinUser/biblioman-calibre/releases/latest` и изтеглете zip файла на плъгина от файловете към изданието.
5. Изберете изтегления zip файл в Calibre.
6. Рестартирайте Calibre.
7. Ако е нужно, включете `Biblioman` сред източниците за метаданни.

## Бележки

- Данните в Biblioman са основно на български.
- Мапването на езиците е умишлено по-консервативно.
- `dist/` съдържа локално генерирани файлове и не се commit-ва.
