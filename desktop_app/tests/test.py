from pathlib import Path
from queue import Queue
from time import sleep
from unittest import mock
from unittest.mock import MagicMock

import pytest
from ereuse_utils.test import AUTH, BASIC, Client
from flask import json
from requests_mock import Mocker

from desktop_app.flaskapp import DesktopApp, WorkbenchThread


def file(name: str) -> dict:
    with Path(__file__).parent.joinpath('fixtures').joinpath(name + '.json').open() as f:
        return json.load(f)


@pytest.fixture()
def mock_snapshot_post(request_mock: Mocker) -> (dict, dict, Mocker):
    """
    Mocks uploading to snapshot (get info and upload).
    You will need to POST to /desktop-app and return info.
    """

    id_test = 0

    # take token from env_dh_test
    headers = {AUTH: BASIC.format('FooToken')}
    request_mock.post('https://foo.com/db-foo/events/devices/snapshot',
                      json={'_id': 'new-snapshot-id'},
                      request_headers=headers)

    return id_test, headers, request_mock


@pytest.fixture()
def workbench() -> MagicMock:
    class WorkbenchDummy:

        def __init__(self) -> None:
            self.snapshot_path = None
            super().__init__()

        def run(self) -> dict:
            # open snapshot file
            return file(self.snapshot_path)

    with mock.patch('desktop_app.flaskapp.Workbench') as mock_workbench:
        mock_workbench.side_effect = WorkbenchDummy()
        yield mock_workbench


@pytest.fixture()
def app() -> DesktopApp:
    return DesktopApp(path_env=Path(__file__).parent.joinpath('fixtures').joinpath('env_dh_test.json'))


@pytest.fixture()
def client(app: DesktopApp):
    return app.test_client()


def test_upload_snapshot_devicehub(client: Client):
    # open snapshot file
    env_test = file('env_dh_test')
    url_snapshot = '{}/{}/events/devices/snapshot'.format(env_test[url], env_test[db])
    response = client.post(uri=url_snapshot, data=snapshot, status=200)

    assert response.status_code == 200


def test_upload_wrong_snapshot_devicehub():
    pass


def test_upload_snapshot_devicehub_wrong_connection():
    wt = WorkbenchThread(Queue())
    wt.snapshot = mock_snapshot_post  # mock snapshot
    wt.upload_to_devicehub()


def test_auto_workbench():
    """Checks that workbench auto-executes when has passed more than X days since the last one."""

    # simulate daysBetweenSnapshots and checks it
    # if (now() - last_snapshot) >= days_between_snapshots:
    #   execute wb
    sleep(1)
    pass


def test_full(workbench: MagicMock, client: Client, mock_snapshot_post: (dict, dict, Mocker)):
    """Test to check if runs workbench and post snapshot correctly"""
    workbench.side_effect.snapshot_path = 'snapshot_test'
    assert workbench.call_count == 0
    # execute workbench
    snapshot, _ = client.get(uri='/workbench', status=200)
    sleep(1)

    # POST Snapshot to Devicehub
    # POST to /desktop-app
    info = client.post(uri='/desktop-app', data=snapshot, status=200)

    # env_test = file('env_dh_test')
    # url_snapshot = '{}/{}/events/devices/snapshot'.format(env_test[url], env_test[db])
    url_snapshot = 'https://foo.com/db-foo/events/devices/snapshot'
    response = client.post(uri=url_snapshot, data=snapshot, status=200)
    # checks to be sure all test works correctly
    assert response.status_code == 200
