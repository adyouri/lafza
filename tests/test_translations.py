# -*- coding: utf-8 -*-
import json

from flask import url_for
import pytest

from project.models import Translation
import base
LENGTH_ERROR = base.length_error(2, 100)


@pytest.mark.usefixtures('client_class')
class TestTranslations:
    def jwt_header(self, username='test'):
        jwt = base.valid_jwt_token(client=self.client, username=username)
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
        """Test adding a new translation"""
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

    def test_upvote_translation(self):
        translation = Translation.query.get(1)
        assert translation.score == 1

        res = self.client.get(
                url_for('main_api.upvote_translation', translation_id=1),
                headers={'Authorization': self.jwt_header()},
                content_type='application/json')
        assert res.status_code == 200
        assert res.json['message'] == ('The translation was'
                                       ' successfully upvoted.')

        assert translation.score == 2

        # Unupvote
        res = self.client.get(
                url_for('main_api.upvote_translation', translation_id=1),
                headers={'Authorization': self.jwt_header()},
                content_type='application/json')
        assert res.status_code == 200
        assert res.json['message'] == ('The translation was'
                                       ' successfully unupvoted.')
        assert translation.score == 1

    def test_downvote_translation(self):
        translation = Translation.query.get(1)
        assert translation.score == 1

        res = self.client.get(
                url_for('main_api.downvote_translation', translation_id=1),
                headers={'Authorization': self.jwt_header()},
                content_type='application/json')
        assert res.status_code == 200
        assert res.json['message'] == ('The translation was'
                                       ' successfully downvoted.')

        assert translation.score == 0

        # Undownvote
        res = self.client.get(
                url_for('main_api.downvote_translation', translation_id=1),
                headers={'Authorization': self.jwt_header()},
                content_type='application/json')
        assert res.status_code == 200
        assert res.json['message'] == ('The translation was'
                                       ' successfully undownvoted.')
        assert translation.score == 1

    @pytest.mark.parametrize('translation_id, user, status_code, message', [

        # The user "test" is not an author nor an admin
        # 1 == "translation"
        (1,
         'test',
         401,
         'Deleting requires to be the author or an admin'
         ),

        # "author_translation"
        (2,
         'test',
         401,
         'Deleting requires to be the author or an admin'
         ),

        # "translation" has no author
        (1,
         'author',
         401,
         'Deleting requires to be the author or an admin'
         ),

        # "author_translation" blongs to the user "author"
        (2,
         'author',
         200,
         'The translation was successfully deleted.'
         ),

        # The admin user "admin" doesn't care who added the translation
        (1,
         'admin',
         200,
         'The translation was successfully deleted.'
         ),

        (2,
         'admin',
         200,
         'The translation was successfully deleted.'
         ),
    ])
    def test_delete_translation(self,
                                translation_id,
                                user,
                                status_code,
                                message):
        res = self.client.delete(
                url_for('main_api.delete_translation',
                        translation_id=translation_id),
                headers={'Authorization': self.jwt_header(user)},
                )
        assert res.status_code == status_code
        assert res.json['message'] == message
