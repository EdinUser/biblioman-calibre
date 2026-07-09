# Biblioman Metadata Source Plugin For Calibre

`biblioman-calibre` is a Calibre metadata download plugin for `https://biblioman.chitanka.info`.

It lets Calibre fetch structured book metadata and cover images from Biblioman, a Bulgarian book catalog maintained by Chitanka. The plugin uses Biblioman's public JSON endpoints instead of scraping HTML, which makes lookups more stable and easier to maintain.

## Download

- Latest release: `https://github.com/EdinUser/biblioman-calibre/releases/latest`
- Direct plugin file in this repository: [`dist/BibliomanMetadata.zip`](dist/BibliomanMetadata.zip)

For most users, the latest GitHub release page is the best download entry point because it always points to the newest packaged plugin version.

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
4. Download the latest plugin zip from `https://github.com/EdinUser/biblioman-calibre/releases/latest` or use [`dist/BibliomanMetadata.zip`](dist/BibliomanMetadata.zip).
5. Select the downloaded zip file in Calibre.
6. Restart Calibre.
7. Enable `Biblioman` in the metadata download sources if needed.

## Notes

- Biblioman metadata is primarily in Bulgarian.
- Language mapping is intentionally conservative.
- `dist/BibliomanMetadata.zip` is the packaged plugin file for direct installation in Calibre.
