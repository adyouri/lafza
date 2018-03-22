# -*- coding: utf-8 -*-
import json

from flask import url_for
import pytest


def test_term_data(term=None, is_acronym=False, full_term=None):
        return json.dumps(dict(
                                term=term,
                                is_acronym=is_acronym,
                                full_term=full_term,
                               ))


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
                'translation': 'translation'}]}

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

    def test_add_full_term(self):
        pass

    def test_failed_add_term(self):
        test_data = json.dumps(dict(
                                term='NTT',
                                full_term='new testing term',
                               ))

        res = self.client.post(url_for('main_api.terms'),
                               data=test_data,
                               content_type='application/json')
        assert b'set is_acronym to true or full_term to null' in res.data

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
