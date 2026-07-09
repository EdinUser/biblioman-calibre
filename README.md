# Biblioman Metadata Source Plugin For Calibre

`biblioman-calibre` is a Calibre metadata download plugin for `https://biblioman.chitanka.info`.

It lets Calibre fetch structured book metadata and cover images from Biblioman, a Bulgarian book catalog maintained by Chitanka. The plugin uses Biblioman's public JSON endpoints instead of scraping HTML, which makes lookups more stable and easier to maintain.

## What This Plugin Does

- searches Biblioman by Biblioman ID, ISBN, title, or title plus first author
- imports title, authors, publisher, publication year, ISBN, comments, tags, and series data
- downloads cover images from Biblioman
- stores a custom `biblioman` identifier in Calibre

## Metadata Fields

The plugin currently maps these Biblioman fields into Calibre:

- title
- authors
- publisher
- publication year as `pubdate`
- ISBN
- comments from the annotation
- tags from genre, themes, and category
- series or sequence
- cover image
- custom identifier `biblioman`

## Data Source

The plugin uses Biblioman's public API-style JSON endpoints:

- `GET /books/{id}.json`
- `GET /books.json?q=...`

This repository is useful if you are looking for:

- a Calibre plugin for Bulgarian books
- a Biblioman metadata source plugin
- a Chitanka Biblioman cover download plugin
- a Python example of a Calibre metadata source plugin

## Project Layout

- `plugin-src/__init__.py` - Calibre plugin source
- `build-plugin.sh` - builds the installable plugin zip
- `dist/BibliomanMetadata.zip` - packaged plugin artifact

## Build

```bash
./build-plugin.sh
```

Build output:

```text
dist/BibliomanMetadata.zip
```

## Install In Calibre

1. Open `Preferences`.
2. Open `Plugins`.
3. Choose `Load plugin from file`.
4. Select `dist/BibliomanMetadata.zip`.
5. Restart Calibre.
6. Enable `Biblioman` in the metadata download sources if needed.

## Notes

- Biblioman metadata is primarily in Bulgarian.
- Language mapping is intentionally conservative.
- The packaged release zip is intended for direct installation in Calibre.
