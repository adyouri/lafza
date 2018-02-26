# -*- coding: utf-8 -*-
import json

from flask import url_for, request
import pytest


@pytest.mark.usefixtures('client_class')
class TestTerms:
    def test_homepage(self):
        res = self.client.get(url_for('main.index'))
        assert res.status_code == 200

    def test_get_terms(self):
        res = self.client.get(url_for('main_api.terms'))
        assert res.status_code == 200
        assert b'Checkbox' in res.data

    def test_get_term(self):
        res = self.client.get(url_for('main_api.term', term='api'))
        res.status_code == 200
        expected_json = {
            'id': 1,
            'term': 'Api',
            'created_date': '2018-01-14T21:00:00.173899',
            'translations': [
                {
                    'translation_id': 1,
                    'translation': 'واجهة برمجية',
                    'created_date': '2018-01-14T21:00:00.177480',
                    'modified_date': '2018-01-14T21:00:00.177500',
                    'score': 1
                }
            ]
        }
        assert res.json == expected_json

    def test_add_term(self):
        res = self.client.get(url_for('main_api.term', term='testing term'))
        assert res.status_code == 404
        test_data = json.dumps(dict(term='testing term'))
        print(test_data)
        # This data is not getting properly sent
        res = self.client.post(url_for('main_api.terms'),
                               data=test_data)
        print('request: ', request.form)
        assert res.status_code == 201
        res = self.client.get(url_for('main_api.term', term='testing term'))
        assert b'testing term' in res.data.lower()
