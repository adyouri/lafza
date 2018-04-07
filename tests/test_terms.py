# -*- coding: utf-8 -*-
import json

from flask import url_for
import pytest


@pytest.mark.usefixtures('client_class')
class TestTerms:
    def test_homepage(self):
        res = self.client.get(url_for('main.index'))
        assert res.status_code == 200

    def test_get_terms(self):
        res = self.client.get(url_for('main_api.terms'))
        assert res.status_code == 200
        assert b'term' in res.data
        assert b'date_created' in res.data

    def test_get_term(self):
        res = self.client.get(url_for('main_api.term', term='term'))
        res.status_code == 200
        expected_json = {
            'author': None,
            'date_created': '2018-01-01T00:00:00+00:00',
            'full_term': None,
            'id': 1,
            'is_acronym': False,
            'term': 'term',
            'translations': [{
                'author': None,
                'date_created': '2018-01-01T00:00:00+00:00',
                'id': 1,
                'modified_date': '2018-01-02T00:00:00+00:00',
                'score': 1,
                'tags': [],
                'term': 1,
                'term_id': 1,
                'translation': 'translation'
            }]}
        assert res.json == expected_json

    def test_add_term(self):
        res = self.client.get(url_for('main_api.term', term='testing term'))
        assert res.status_code == 404
        test_data = json.dumps(dict(term='testing term'))
        res = self.client.post(url_for('main_api.terms'),
                               data=test_data,
                               content_type='application/json')
        assert res.status_code == 201
        res = self.client.get(url_for('main_api.term', term='testing term'))
        assert b'testing term' in res.data.lower()

    def test_term_exists(self):
        self.test_add_term()
        # Add the term again
        test_data = json.dumps(dict(term='testing term'))
        res = self.client.post(url_for('main_api.terms'),
                               data=test_data,
                               content_type='application/json')
        assert res.status_code == 400
        assert b'testing term already exists' in res.data
        assert b'/terms/testing%20term' in res.data

    # Add term using parametrization
    @pytest.mark.parametrize('term_data, status_code, message', [
        (('testing term', None, False), 201, 'testing term'),
        (('TT', 'testing term', True), 201, 'TT'),
        (('TT', 'testing term', False), 400, 'set is_acronym to true'),
        (('TT', None, True), 400, 'set is_acronym to false'),
        (('', '', ''), 400, 'Not a valid boolean'),
        ((None, None, None), 400, 'Field may not be null.'),
        (('T', 'testing term', True), 400, 'Shorter than minimum length'),
        (('TT', 't', True), 400, 'Shorter than minimum length'),
        (('T', 't', True), 400, 'Shorter than minimum length'),
    ])
    def test_add_term_with_params(self, term_data, status_code, message):
        term, full_term, is_acronym = term_data
        term_data = json.dumps(dict(
                    term=term,
                    is_acronym=is_acronym,
                    full_term=full_term,
                    ))
        res = self.client.post(url_for('main_api.terms'),
                               data=term_data,
                               content_type='application/json')
        assert res.status_code == status_code
        assert message.encode(encoding='UTF-8') in res.data
