# Biblioman Calibre Plugin

Calibre metadata-source plugin for `https://biblioman.chitanka.info`.

The plugin uses Biblioman's public JSON endpoints instead of scraping HTML:

- `GET /books/{id}.json`
- `GET /books.json?q=...`

It currently imports:

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

## Layout

- `plugin-src/__init__.py` - the Calibre plugin module
- `build-plugin.sh` - builds an installable zip in `dist/`

## Build

Run:

```bash
./build-plugin.sh
```

This creates:

```text
dist/BibliomanMetadata.zip
```

## Install In Calibre

1. Open `Preferences`.
2. Open `Plugins`.
3. Choose `Load plugin from file`.
4. Select `dist/BibliomanMetadata.zip`.
5. Restart Calibre.

Then enable `Biblioman` under metadata download sources.

## Notes

- The plugin can identify books by Biblioman ID, ISBN, title, or title plus first author.
- Biblioman uses Bulgarian-language metadata, so language mapping is intentionally conservative.
- I could not run this inside a local Calibre environment here, so the code is scaffolded against the current Calibre plugin API and the live Biblioman JSON responses, but not runtime-tested in Calibre itself.
