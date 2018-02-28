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
        assert b'Term' in res.data
        assert b'created_date' in res.data

    def test_get_term(self):
        res = self.client.get(url_for('main_api.term', term='term'))
        res.status_code == 200
        expected_json = {
            'id': 1,
            'term': 'Term',
            'created_date': '2018-01-01T00:00:00',
            'translations': [
                {
                    'translation_id': 1,
                    'translation': 'translation',
                    'created_date': '2018-01-01T00:00:00',
                    'modified_date': '2018-01-02T00:00:00',
                    'score': 1
                }
            ]
        }
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
