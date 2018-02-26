# -*- coding: utf-8 -*-
from flask import url_for


def test_homepage(client):
    res = client.get(url_for('main.index'))
    assert res.status_code == 200
