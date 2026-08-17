import importlib.util
import sys
import types
import unittest
from pathlib import Path


def load_plugin():
    calibre = types.ModuleType('calibre')
    calibre.prepare_string_for_xml = lambda value: value

    metadata = types.ModuleType('calibre.ebooks.metadata')
    metadata.check_isbn = lambda value: value or None

    book_base = types.ModuleType('calibre.ebooks.metadata.book.base')
    book_base.Metadata = type('Metadata', (), {})

    source_base = types.ModuleType('calibre.ebooks.metadata.sources.base')
    source_base.Source = type('Source', (), {})

    class Option:
        def __init__(self, name, type_, default, label, desc, choices=None):
            self.name = name
            self.type = type_
            self.default = default
            self.label = label
            self.desc = desc
            self.choices = choices

    source_base.Option = Option

    localization = types.ModuleType('calibre.utils.localization')
    localization._ = lambda value: value

    sys.modules.update({
        'calibre': calibre,
        'calibre.ebooks': types.ModuleType('calibre.ebooks'),
        'calibre.ebooks.metadata': metadata,
        'calibre.ebooks.metadata.book': types.ModuleType('calibre.ebooks.metadata.book'),
        'calibre.ebooks.metadata.book.base': book_base,
        'calibre.ebooks.metadata.sources': types.ModuleType('calibre.ebooks.metadata.sources'),
        'calibre.ebooks.metadata.sources.base': source_base,
        'calibre.utils': types.ModuleType('calibre.utils'),
        'calibre.utils.localization': localization,
    })

    source_path = Path(__file__).parents[1] / 'plugin-src' / '__init__.py'
    spec = importlib.util.spec_from_file_location('biblioman_plugin', source_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PLUGIN = load_plugin()


class Abort:
    def is_set(self):
        return False


class SearchFlowTest(unittest.TestCase):
    title = 'Голямото слънце на Меркурий'
    author = 'Айзък Азимов'

    def setUp(self):
        self.source = PLUGIN.Biblioman()
        self.abort = Abort()

    def test_title_search_uses_plain_title_and_accepts_subtitle_match(self):
        calls = []
        target = {
            'id': 14060,
            'title': 'Врагът от Сириус',
            'subtitle': self.title,
            'author': self.author,
        }

        def search(log, query, timeout):
            calls.append(query)
            return [target]

        self.source._search = search
        self.source._search_author_for_title = self.fail

        candidates = self.source._identify_books(
            None, self.abort, title=self.title, authors=[self.author], identifiers={}
        )

        self.assertEqual([14060], [book['id'] for book in candidates])
        self.assertEqual([self.title], calls)

    def test_multiple_title_matches_are_ranked_by_author(self):
        other_author = {
            'id': 1,
            'title': self.title,
            'author': 'Друг автор',
        }
        requested_author = {
            'id': 2,
            'title': self.title,
            'author': self.author,
        }
        self.source._search = lambda log, query, timeout: [other_author, requested_author]
        self.source._search_author_for_title = self.fail

        candidates = self.source._identify_books(
            None, self.abort, title=self.title, authors=[self.author], identifiers={}
        )

        self.assertEqual([2, 1], [book['id'] for book in candidates])

    def test_author_fallback_is_used_only_when_title_search_has_no_match(self):
        target = {
            'id': 14060,
            'title': 'Врагът от Сириус',
            'subtitle': self.title,
            'author': self.author,
        }
        author_queries = []
        self.source._search = lambda log, query, timeout: [
            {'id': 1, 'title': 'Несвързана книга', 'author': self.author}
        ]

        def search_author_for_title(log, query, title, timeout, abort):
            author_queries.append(query)
            return [target]

        self.source._search_author_for_title = search_author_for_title

        candidates = self.source._identify_books(
            None, self.abort, title=self.title, authors=[self.author], identifiers={}
        )

        self.assertEqual([14060], [book['id'] for book in candidates])
        self.assertEqual(['author: %s' % self.author], author_queries)

    def test_no_credible_title_match_returns_no_candidate(self):
        self.source._search = lambda log, query, timeout: []
        self.source._search_author_for_title = lambda log, query, title, timeout, abort: []

        candidates = self.source._identify_books(
            None, self.abort, title=self.title, authors=[self.author], identifiers={}
        )

        self.assertEqual([], candidates)

    def test_author_fallback_stops_at_the_first_matching_page(self):
        query = 'author: %s' % self.author
        base_url = self.source.SEARCH_URL % PLUGIN.quote_plus(query)
        responses = {
            base_url: {'results': [{'id': 1, 'title': 'Несвързана книга'}], 'nbPages': 3},
            '%s&page=2' % base_url: {
                'results': [{'id': 2, 'title': self.title}], 'nbPages': 3
            },
            '%s&page=3' % base_url: {
                'results': [{'id': 3, 'title': self.title}], 'nbPages': 3
            },
        }
        requested_urls = []

        def get_json(log, url, timeout):
            requested_urls.append(url)
            return responses[url]

        self.source._get_json = get_json

        books = self.source._search_author_for_title(
            None, query, self.title, 30, self.abort
        )

        self.assertEqual([2], [book['id'] for book in books])
        self.assertEqual([base_url, '%s&page=2' % base_url], requested_urls)

    def test_author_series_is_preferred_over_publisher_series(self):
        series_name, series_index = self.source._series_data({
            'series': 'Бараяр (Barrayar)',
            'seriesNr': '10',
            'sequence': 'Избрана световна фантастика',
            'sequenceNr': '71',
        })

        self.assertEqual('Бараяр (Barrayar)', series_name)
        self.assertEqual(10.0, series_index)

    def test_series_download_option_defaults_to_disabled(self):
        option = PLUGIN.Biblioman.options[0]

        self.assertEqual('download_series', option.name)
        self.assertFalse(option.default)

    def test_series_download_option_can_preserve_existing_series(self):
        class Metadata:
            def __init__(self, title, authors):
                self.title = title
                self.authors = authors
                self.identifiers = {}

        original_metadata = PLUGIN.Metadata
        PLUGIN.Metadata = Metadata
        self.source.prefs = {'download_series': False}
        self.source.clean_downloaded_metadata = lambda mi: None
        try:
            mi = self.source._book_to_metadata({
                'id': 1,
                'title': 'Братя по оръжие',
                'author': 'Лоис Макмастър Бюджолд',
                'series': 'Бараяр (Barrayar)',
                'seriesNr': '10',
            }, 0, None)
        finally:
            PLUGIN.Metadata = original_metadata

        self.assertFalse(hasattr(mi, 'series'))
        self.assertFalse(hasattr(mi, 'series_index'))


if __name__ == '__main__':
    unittest.main()
