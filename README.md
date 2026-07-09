# Biblioman плъгин за Calibre

`biblioman-calibre` е плъгин за Calibre, който изтегля метаданни и корици от `https://biblioman.chitanka.info`.

С него Calibre може да намира структурирани данни за книги от Biblioman, каталога за книги на Читанка. Плъгинът използва публичните JSON адреси на Biblioman, а не HTML страниците, което прави търсенето по-стабилно и по-лесно за поддръжка.

## Изтегляне

- Latest release: `https://github.com/EdinUser/biblioman-calibre/releases/latest`
- Директен файл в хранилището: [`dist/BibliomanMetadata.zip`](dist/BibliomanMetadata.zip)

За повечето хора страницата с latest release е най-удобният вариант, защото винаги сочи към последната готова версия на плъгина.

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
- `dist/BibliomanMetadata.zip` - готовият файл за инсталиране в Calibre

## Build

```bash
./build-plugin.sh
```

Резултатът е:

```text
dist/BibliomanMetadata.zip
```

## Инсталиране в Calibre

1. Отворете `Preferences`.
2. Отворете `Plugins`.
3. Изберете `Load plugin from file`.
4. Изтеглете последния zip файл от `https://github.com/EdinUser/biblioman-calibre/releases/latest` или използвайте [`dist/BibliomanMetadata.zip`](dist/BibliomanMetadata.zip).
5. Изберете изтегления zip файл в Calibre.
6. Рестартирайте Calibre.
7. Ако е нужно, включете `Biblioman` сред източниците за метаданни.

## Бележки

- Данните в Biblioman са основно на български.
- Мапването на езиците е умишлено по-консервативно.
- `dist/BibliomanMetadata.zip` е файлът за директно инсталиране в Calibre.
