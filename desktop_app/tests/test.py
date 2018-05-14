from pathlib import Path
from queue import Queue

import requests
from flask import json
from pathlib import Path
from ereuse_utils.test import Client

# mocks:
# - workbench: Workbench()
# - devicehub (requests)

from desktop_app.flaskapp import DesktopApp, WorkbenchThread


class WorkbenchDummy:
    snapshot = None

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> dict:
        return ## open snapshot file and return a dict


def test_upload_snapshot_devicehub():
    pass

def test_upload_wrong_snapshot_devicehub():
    pass

def test_upload_snapshot_devicehub_wrong_connection():
    wt = WorkbenchThread(Queue())
    wt.snapshot = # mock snapshot
    wt.upload_to_devicehub()


def test_auto_workbench():
    """Checks that workbench auto-executes when has passed more than X days since the last one."""


def test_workbench_post_snapshot():
    """Test to check if runs workbench and post snapshot correctly"""
    app = DesktopApp()
    client = app.test_client()  # type: Client
    snapshot, _ = client.get(uri='/workbench', status=200)
    sleep(1)




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

