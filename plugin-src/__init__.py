#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import re
from datetime import datetime, timezone

try:
    from queue import Empty, Queue
except ImportError:
    from Queue import Empty, Queue

try:
    from urllib.parse import quote_plus, urlparse
except ImportError:
    from urllib import quote_plus
    from urlparse import urlparse

from calibre import prepare_string_for_xml
from calibre.ebooks.metadata import check_isbn
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.sources.base import Source
from calibre.utils.localization import _


class Biblioman(Source):

    name = 'Biblioman'
    description = _('Downloads metadata and covers from biblioman.chitanka.info')
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Edin User'
    version = (0, 1, 0)
    minimum_calibre_version = (6, 0, 0)

    capabilities = frozenset(['identify', 'cover'])
    touched_fields = frozenset([
        'title',
        'authors',
        'tags',
        'pubdate',
        'comments',
        'publisher',
        'series',
        'languages',
        'identifier:isbn',
        'identifier:biblioman',
    ])
    supports_gzip_transfer_encoding = True
    cached_cover_url_is_reliable = True
    prefer_results_with_isbn = True
    can_get_multiple_covers = False

    BASE_URL = 'https://biblioman.chitanka.info'
    SEARCH_URL = BASE_URL + '/books.json?q=%s'
    BOOK_URL = BASE_URL + '/books/%s'
    BOOK_JSON_URL = BASE_URL + '/books/%s.json'
    ID_REGEX = re.compile(r'/books/(\d+)(?:\.[a-z0-9]+)?$', re.IGNORECASE)
    YEAR_REGEX = re.compile(r'^\d{4}$')
    LANGUAGE_MAP = {
        'български': 'bul',
        'английски': 'eng',
        'руски': 'rus',
        'немски': 'deu',
        'френски': 'fra',
        'испански': 'spa',
        'италиански': 'ita',
        'полски': 'pol',
        'чешки': 'ces',
        'сръбски': 'srp',
        'хърватски': 'hrv',
        'македонски': 'mkd',
        'гръцки': 'ell',
        'турски': 'tur',
        'латински': 'lat',
    }

    def get_book_url(self, identifiers):
        biblioman_id = identifiers.get('biblioman')
        if biblioman_id:
            return ('biblioman', biblioman_id, self.BOOK_URL % biblioman_id)

    def id_from_url(self, url):
        parsed = urlparse(url)
        if parsed.netloc != 'biblioman.chitanka.info':
            return None
        match = self.ID_REGEX.search(parsed.path or '')
        if match:
            return ('biblioman', match.group(1))
        return None

    def get_cached_cover_url(self, identifiers):
        biblioman_id = identifiers.get('biblioman')
        if biblioman_id is None:
            isbn = check_isbn(identifiers.get('isbn'))
            if isbn is not None:
                biblioman_id = self.cached_isbn_to_identifier(isbn)
        if biblioman_id is None:
            return None
        return self.cached_identifier_to_cover_url(str(biblioman_id))

    def identify(
        self,
        log,
        result_queue,
        abort,
        title=None,
        authors=None,
        identifiers={},
        timeout=30,
    ):
        candidates = self._identify_books(
            log,
            abort,
            title=title,
            authors=authors,
            identifiers=identifiers,
            timeout=timeout,
        )
        for index, book in enumerate(candidates):
            if abort.is_set():
                break
            mi = self._book_to_metadata(book, index, log)
            if mi is not None:
                result_queue.put(mi)

    def download_cover(
        self,
        log,
        result_queue,
        abort,
        title=None,
        authors=None,
        identifiers={},
        timeout=30,
        get_best_cover=False,
    ):
        if abort.is_set():
            return

        cover_url = self.get_cached_cover_url(identifiers)
        if not cover_url:
            rq = Queue()
            self.identify(
                log,
                rq,
                abort,
                title=title,
                authors=authors,
                identifiers=identifiers,
                timeout=timeout,
            )
            while True:
                try:
                    mi = rq.get_nowait()
                except Empty:
                    break
                cover_url = self.get_cached_cover_url(mi.identifiers)
                if cover_url:
                    break

        if not cover_url:
            log.info('No Biblioman cover found')
            return

        try:
            cdata = self.browser.open_novisit(cover_url, timeout=timeout).read()
            if cdata:
                result_queue.put((self, cdata))
        except Exception:
            log.exception('Failed to download cover from:', cover_url)

    def _identify_books(self, log, abort, title=None, authors=None, identifiers={}, timeout=30):
        seen = set()
        candidates = []
        biblioman_id = identifiers.get('biblioman')
        isbn = check_isbn(identifiers.get('isbn'))

        if biblioman_id:
            book = self._fetch_book(log, biblioman_id, timeout)
            if book:
                candidates.append(book)
                seen.add(book.get('id'))

        queries = []
        if isbn:
            queries.append('isbn: %s' % isbn)
        text_query = self._build_text_query(title, authors)
        if text_query:
            queries.append(text_query)
        if title:
            queries.append('title: %s' % title)
        if authors:
            queries.append('author: %s' % authors[0])

        for query in queries:
            if abort.is_set():
                break
            for book in self._search(log, query, timeout):
                book_id = book.get('id')
                if not book_id or book_id in seen:
                    continue
                seen.add(book_id)
                candidates.append(book)

        return sorted(
            candidates,
            key=lambda book: self._sort_key(book, title=title, authors=authors, isbn=isbn),
            reverse=True,
        )[:10]

    def _fetch_book(self, log, biblioman_id, timeout):
        return self._get_json(log, self.BOOK_JSON_URL % biblioman_id, timeout)

    def _search(self, log, query, timeout):
        data = self._get_json(log, self.SEARCH_URL % quote_plus(query), timeout)
        if not data:
            return []
        return data.get('results') or []

    def _get_json(self, log, url, timeout):
        try:
            raw = self.browser.open_novisit(url, timeout=timeout).read()
            if not isinstance(raw, str):
                raw = raw.decode('utf-8')
            return json.loads(raw)
        except Exception:
            log.exception('Failed to fetch Biblioman JSON from:', url)
            return None

    def _book_to_metadata(self, book, relevance, log):
        title = self._compose_title(book)
        authors = self._split_people(book.get('author'))
        if not title:
            return None
        if not authors:
            authors = [_('Unknown')]

        mi = Metadata(title, authors)
        mi.source_relevance = relevance
        mi.identifiers = {}

        biblioman_id = book.get('id')
        if biblioman_id:
            mi.identifiers['biblioman'] = str(biblioman_id)

        isbn = check_isbn(book.get('isbn'))
        if isbn:
            mi.isbn = isbn
            mi.identifiers['isbn'] = isbn
            if biblioman_id:
                self.cache_isbn_to_identifier(isbn, str(biblioman_id))

        publisher = self._clean_value(book.get('publisher'))
        if publisher:
            mi.publisher = publisher

        comments = self._format_comments(book.get('annotation'))
        if comments:
            mi.comments = comments

        language = self._map_language(book.get('language'))
        if language:
            mi.language = language

        pubdate = self._parse_year(book.get('publishingYear'))
        if pubdate is not None:
            mi.pubdate = pubdate

        tags = self._collect_tags(book)
        if tags:
            mi.tags = tags

        series_name, series_index = self._series_data(book)
        if series_name:
            mi.series = series_name
            if series_index is not None:
                mi.series_index = series_index

        cover_url = self._cover_url(book)
        if cover_url and biblioman_id:
            self.cache_identifier_to_cover_url(str(biblioman_id), cover_url)

        try:
            self.clean_downloaded_metadata(mi)
        except Exception:
            log.exception('Failed to clean Biblioman metadata')
        return mi

    def _sort_key(self, book, title=None, authors=None, isbn=None):
        score = 0
        if isbn and check_isbn(book.get('isbn')) == isbn:
            score += 100

        wanted_title = self._normalize_text(title)
        candidate_title = self._normalize_text(self._compose_title(book))
        if wanted_title and candidate_title:
            if wanted_title == candidate_title:
                score += 50
            elif wanted_title in candidate_title or candidate_title in wanted_title:
                score += 30

        wanted_author = self._normalize_text((authors or [None])[0])
        candidate_author = self._normalize_text(book.get('author'))
        if wanted_author and candidate_author:
            if wanted_author == candidate_author:
                score += 25
            elif wanted_author in candidate_author or candidate_author in wanted_author:
                score += 15

        if book.get('cover'):
            score += 3
        if book.get('annotation'):
            score += 2
        return score

    def _compose_title(self, book):
        parts = []
        for key in ('title', 'volumeTitle', 'subtitle', 'subtitle2'):
            value = self._clean_value(book.get(key))
            if value:
                parts.append(value)
        if not parts:
            return None
        title = parts[0]
        for part in parts[1:]:
            title = '%s: %s' % (title, part)
        return title

    def _series_data(self, book):
        series_name = self._clean_value(book.get('series')) or self._clean_value(book.get('sequence'))
        if not series_name:
            return (None, None)
        raw_index = book.get('seriesNr') or book.get('sequenceNr')
        try:
            return (series_name, float(raw_index))
        except (TypeError, ValueError):
            return (series_name, None)

    def _cover_url(self, book):
        urls = book.get('urls') or {}
        cover_path = urls.get('cover') or urls.get('coverSmall') or urls.get('coverMini')
        if not cover_path:
            return None
        if cover_path.startswith('http://') or cover_path.startswith('https://'):
            return cover_path
        return self.BASE_URL + cover_path

    def _collect_tags(self, book):
        tags = []
        for value in (book.get('genre'), book.get('themes')):
            for tag in self._split_multi_value(value):
                if tag not in tags:
                    tags.append(tag)

        category = book.get('category') or {}
        category_name = self._clean_value(category.get('name'))
        if category_name and category_name not in tags:
            tags.append(category_name)
        return tags

    def _map_language(self, value):
        value = self._clean_value(value)
        if not value:
            return None
        return self.LANGUAGE_MAP.get(value.lower())

    def _parse_year(self, value):
        value = self._clean_value(value)
        if not value or not self.YEAR_REGEX.match(value):
            return None
        return datetime(int(value), 1, 1, tzinfo=timezone.utc)

    def _format_comments(self, value):
        value = self._clean_value(value)
        if not value:
            return None
        paragraphs = []
        for paragraph in re.split(r'\n\s*\n', value):
            paragraph = paragraph.strip()
            if paragraph:
                paragraph = prepare_string_for_xml(paragraph).replace('\n', '<br/>')
                paragraphs.append('<p>%s</p>' % paragraph)
        return '\n'.join(paragraphs) or None

    def _build_text_query(self, title, authors):
        parts = []
        if title:
            parts.append(title)
        if authors:
            parts.append(authors[0])
        return ' '.join(part for part in parts if part).strip() or None

    def _split_people(self, value):
        return self._split_multi_value(value)

    def _split_multi_value(self, value):
        value = self._clean_value(value)
        if not value:
            return []
        parts = [part.strip() for part in value.split(';')]
        return [part for part in parts if part]

    def _clean_value(self, value):
        if value is None:
            return None
        value = value.strip() if hasattr(value, 'strip') else value
        return value or None

    def _normalize_text(self, value):
        value = self._clean_value(value)
        if not value:
            return ''
        value = value.lower()
        return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]+', ' ', value, flags=re.UNICODE)).strip()
