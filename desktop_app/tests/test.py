import requests
from flask import json


class TestClass(object):

    def test_post_snapshot(self):
        """Test to check if works login Devicetag and post snapshot correctly"""
        self.env = json.loads('env_dh_test.json')

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

    def test_workbench(self):
        x = "hello"
        assert hasattr(x, 'check')

    def post_json(client, url, json_dict):
        """Send dictionary json_dict as a json to the specified url """
        return client.post(url, data=json.dumps(json_dict), content_type='application/json')

    def json_of_response(response):
        """Decode json from response"""
        return json.loads(response.data.decode('utf8'))
