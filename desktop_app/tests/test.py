from pathlib import Path

import requests
from flask import json
from pathlib import Path
from ereuse_utils.test import Client


class TestClass(object):

    def test_workbench_post_snapshot(self):
        """Test to check if runs workbench and post snapshot correctly"""
        with Path(__file__).parent.joinpath('fixtures/.env_dh_test.json').open('w') as file:
            self.config = json.load(file)  # type: dict

        # login devicehub
        # POST Login to get auth
        data_login = env[login]
        response = requests.post(url_local, json=data_login, headers=headers)

        db = response.json()

        # upload snapshot
        # POST Snapshot to Devicehub
        url_snapshot = '{}/{}/events/devices/snapshot'.format('localhost', db)
        with open('snapshot_test.json') as t:
            snapshot_test = json.load(t)

        r = requests.post(url_snapshot, json=snapshot_test, headers=headers_snapshot)

        assert {'key': 'value'} in r.data
        assert r.status_code == 200
