# -*- coding: utf-8 -*-
import json

from flask import url_for
import pytest


@pytest.mark.usefixtures('client_class')
class TestTranslations:
    def test_get_translations(self):
        res = self.client.get(url_for('main_api.translations'))
        assert res.status_code == 200
        assert b'translation' in res.data
        assert b'created_date' in res.data

    def test_add_translation(self):
        res = self.client.get(url_for('main_api.term',
                              term='term'))
        assert b'testing term translation' not in res.data
        test_data = json.dumps(dict(translation='testing term translation',
                                    term_id=1))
        res = self.client.post(url_for('main_api.translations'),
                               data=test_data,
                               content_type='application/json')
        assert res.status_code == 201  # Added
        res = self.client.get(url_for('main_api.term',
                              term='term'))
        assert b'testing term translation' in res.data.lower()

    def test_translation_exists(self):
        self.test_add_translation()
        # Add the translation again
        test_data = json.dumps(dict(translation='testing term translation',
                               term_id=1))
        res = self.client.post(url_for('main_api.translations'),
                               data=test_data,
                               content_type='application/json')
        assert res.status_code == 400
        assert b'testing term translation already exists' in res.data
