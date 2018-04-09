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
        assert b'date_created' in res.data

    def test_add_translation(self):
        res = self.client.get(url_for('main_api.term',
                              term='term'))
        assert b'testing term translation' not in res.data
        test_data = json.dumps(dict(translation='testing term translation',
                                    term_id=1))
        res = self.client.post(url_for('main_api.translations'),
                               data=test_data,
                               content_type='application/json')

        assert b'testing term translation' in res.data.lower()

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
        assert b'Translation already exists' in res.data

    # Add translation using parametrization
    @pytest.mark.parametrize('translation,\
            term_id,\
            tags,\
            status_code,\
            message', [
                ('testing translation', 3, None, 400, 'Term does not exist'),
                ('testing translation', 1, [], 201, 'testing translation'),
                ('testing translation',
                 1, ['testing_tag'], 201,
                 '"tags": [\n                1\n            ]'),
                ('testing translation',
                 1, ['testing_tag', 'tag2'], 201,
                 '[\n                1,\n                2\n            ]'),
        ])
    def test_parametrized_add_translation(self,
                                          translation,
                                          term_id,
                                          tags,
                                          status_code,
                                          message):
        '''Test adding a new translation'''
        translation_data = json.dumps(dict(
                                      translation=translation,
                                      term_id=term_id,
                                      tags=tags,
                                      status_code=status_code,
                                      message=message,
                                      ))

        res = self.client.post(url_for('main_api.translations'),
                               data=translation_data,
                               content_type='application/json')

        assert res.status_code == status_code
        assert message.encode(encoding='UTF-8') in res.data
