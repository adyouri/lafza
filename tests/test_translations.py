# -*- coding: utf-8 -*-
import json

from flask import url_for
import pytest

import base
LENGTH_ERROR = base.length_error(2, 100)


@pytest.mark.usefixtures('client_class')
class TestTranslations:
    def jwt_header(self):
        jwt = base.valid_jwt_token(client=self.client)
        return jwt

    def test_get_translations(self):
        res = self.client.get(
                url_for('main_api.translations'),
                headers={'Authorization': self.jwt_header()},
                )
        assert res.status_code == 200
        assert b'translation' in res.data
        assert b'date_created' in res.data

    def test_failed_add_translation(self):
        test_data = json.dumps(dict(translation='testing term translation',
                                    term_id=1))
        res = self.client.post(url_for('main_api.translations'),
                               data=test_data,
                               content_type='application/json')
        assert res.status_code == 401

    def test_add_translation(self):
        res = self.client.get(
                              url_for('main_api.term', term='term'),
                              headers={'Authorization': self.jwt_header()},
                              )

        assert b'testing term translation' not in res.data
        test_data = json.dumps(dict(translation='testing term translation',
                                    term_id=1))
        res = self.client.post(url_for('main_api.translations'),
                               data=test_data,
                               headers={'Authorization': self.jwt_header()},
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
                               headers={'Authorization': self.jwt_header()},
                               content_type='application/json')
        assert res.status_code == 400
        assert b'Translation already exists' in res.data

    # Add translation using parametrization
    @pytest.mark.parametrize('translation,\
            term_id,\
            tags,\
            status_code,\
            message', [
                ('t', 1, None, 400, LENGTH_ERROR),
                ('t'*101, 1, None, 400, LENGTH_ERROR),
                ('testing translation', 3, None, 400, 'Term does not exist'),
                ('testing translation', 1, [], 201, 'testing translation'),
                ('translation1', 1, ['test_tag'], 201, 'translation1'),
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
                                      date_created='2018-01-11T15:43:00',
                                      modified_date='2018-01-11T15:43:00'
                                      ))

        res = self.client.post(url_for('main_api.translations'),
                               data=translation_data,
                               headers={'Authorization': self.jwt_header()},
                               content_type='application/json')

        assert res.status_code == status_code
        assert message.encode(encoding='UTF-8') in res.data
        if res.status_code == 201:
            # Test creation and modification dates are read-only
            date_created = res.json['translations'][1]['date_created']
            modified_date = res.json['translations'][1]['modified_date']
            assert date_created != '2018-01-11T15:43:00+00:00'
            assert modified_date != '2018-01-11T15:43:00+00:00'
            # Test translation author
            assert res.json['translations'][1]['author'] == 1
