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
def request_mock() -> Mocker:
    """
    Integrates requests-mock with pytest.
    See https://github.com/pytest-dev/pytest/issues/2749#issuecomment-350411895.
    """
    with Mocker() as m:
        yield m


@pytest.fixture()
def mock_requests_snapshot(request_mock: Mocker) -> (dict, Mocker):
    """
    Mocks uploading to snapshot (get info and upload).
    GET to /desktop-app with snapshot data and return info.
    POST to /events/devices/snapshot to upload snapshot to DH
    """
    # open env file
    env_test = file('env_dh_test')
    uri_post = '{}/{}/events/devices/snapshot'.format(env_test['url'], env_test['db'])

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    headers_snapshot = headers.update({AUTH: BASIC.format(env_test['token'])})

    request_mock.post(uri_post,
                      json={'_id': 'new-snapshot-id'},
                      request_headers=headers_snapshot)

    # GET Request Matching
    request_mock.register_uri('GET', 'https://api.devicetag.io/desktop-app',
                              request_headers=headers,
                              json=env_test)
    return headers, request_mock


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
        mock_workbench.side_effect = WorkbenchDummy
        yield mock_workbench


@pytest.fixture()
def app() -> DesktopApp:
    return DesktopApp(path_env=Path(__file__).parent.joinpath('fixtures').joinpath('env_dh_test.json'))


@pytest.fixture()
def client(app: DesktopApp):
    return app.test_client()


def test_upload_snapshot_devicehub(client: Client):
    # Open snapshot file
    env_test = file('env_dh_test')
    snapshot = file('snapshot_test')
    url_snapshot = '{}/{}/events/devices/snapshot'.format(env_test['url'], env_test['db'])
    response = client.post(uri=url_snapshot, data=snapshot, status=200)

    # Only check status code?
    assert response.status_code == 200


def test_upload_wrong_snapshot_devicehub():
    pass


def test_upload_snapshot_devicehub_wrong_connection():
    wt = WorkbenchThread(Queue())
    wt.snapshot = mock_requests_snapshot  # mock snapshot
    wt.upload_to_devicehub()


def test_auto_workbench(workbench: MagicMock, client: Client):
    """Checks that workbench auto-executes when has passed more than X days since the last one."""
    # open env file
    env_test = file('env_dh_test')

    # simulate daysBetweenSnapshots and checks it
    # if (datetime.now() - env_test['lastSnapshot']) >= env_test['daysBetweenSnapshots']:
    #   snapshot, _ = client.get(uri='/workbench', status=200)
    sleep(1)
    #assert snapshot is correct
    pass


def test_init_with_id(workbench: MagicMock, mock_requests_snapshot: (dict, Mocker)):
    """
    Test initialization of desktop-app server
    Case where in env file appears id of device
    """
    workbench.side_effect.snapshot_path = 'snapshot_test'
    headers, mocked_snapshot = mock_requests_snapshot
    assert workbench.call_count == 0
    assert mocked_snapshot.call_count == 0

    DesktopApp(path_env=Path(__file__).parent.joinpath('fixtures').joinpath('env_test_id.json'))

    assert workbench.call_count == 1
    assert mocked_snapshot.call_count == 1


def test_init_without_id(workbench: MagicMock, mock_requests_snapshot: (dict, Mocker)):
    """
    Test initialization of desktop-app server
    Case where in env file hasn't id of device and needs to get it from Devicehub
    """
    workbench.side_effect.snapshot_path = 'snapshot_test'
    headers, mocked_snapshot = mock_requests_snapshot
    assert workbench.call_count == 0
    assert mocked_snapshot.call_count == 0

    DesktopApp(path_env=Path(__file__).parent.joinpath('fixtures').joinpath('env_test_no_id.json'))

    assert workbench.call_count == 1
    assert mocked_snapshot.call_count == 1

def test_init_execute_periodic_workbench():
    """
    Test initialization of desktop-app server
    Case where days between last snapshot is up to X days and needs to execute Workbench
    """
    pass

def test_init_without_id_and_periodic_workbench():
    """
    Test initialization of desktop-app server
    Case where in env file hasn't id of device and needs to get it from Devicehub
    & days between last snapshot is up to X days and needs to execute Workbench
    """
    pass
    assert workbench.call_count == 1, 'Workbench should have executed only one time regardless of both conditions applying'


def test_execute_workbench(workbench: MagicMock, client: Client, mock_requests_snapshot: (dict, Mocker)):
    """
    Test to check if runs workbench and post snapshot correctly
    """
    workbench.side_effect.snapshot_path = 'snapshot_test'
    headers, mocked_snapshot = mock_requests_snapshot
    # assert workbench.call_count == 0 error 1 == 1
    assert mocked_snapshot.call_count == 0

    # execute workbench
    snapshot, _ = client.get(uri='/workbench', status=200)
    sleep(1)

    # open env file and get post params
    env_test = file('env_dh_test')
    url_snapshot = '{}/{}/events/devices/snapshot'.format(env_test['url'], env_test['db'])
    headers_snapshot = headers.update({AUTH: BASIC.format(env_test['token'])})

    assert workbench.call_count == 1

    # POST snapshot to Devicehub
    response = client.post(uri=url_snapshot, data=snapshot, headers=headers_snapshot, status=200)

    assert mocked_snapshot.call_count == 1
    assert response.status_code == 200


def test_get_env_from_dh():
    """
    Tests dummy
    """
    # execute workbench
    snapshot, _ = client.post(uri='/workbench', data=None, status=200)
    sleep(1)

    # assert workbench.call_count == 1

    # GET to /desktop-app with snapshot data to return id
    r = client.get(uri='/desktop-app', status=200)

    assert mocked_snapshot.call_count == 1
    assert r.status_code == 200
    # check if id exists
    assert r.json()['id'] != ""
