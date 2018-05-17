import json
from datetime import datetime, timedelta
from multiprocessing import Queue
from pathlib import Path
from threading import Thread

import requests
from dateutil.parser import parse
from ereuse_utils import ensure_utf8, DeviceHubJSONEncoder
from ereuse_utils.test import Client
from ereuse_workbench.workbench import Workbench
from flask import Flask, render_template, jsonify, request, Response


class DesktopApp(Flask):
    """ todo Systemd root service desktop-app
        todo python scheduler per correr periodicament
        todo create icon.desktop
    """

    test_client_class = Client
    json_encoder = DeviceHubJSONEncoder

    def __init__(self,
                 import_name=__name__,
                 static_path=None,
                 static_url_path=None,
                 static_folder='static',
                 template_folder='templates',
                 instance_path=None,
                 instance_relative_config=False,
                 root_path=None,
                 path_env=Path(__file__).parent.joinpath('.env_dh.json')
                 ):
        ensure_utf8(self.__class__.__name__)
        super().__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                         instance_path, instance_relative_config, root_path)
        self.add_url_rule('/', view_func=self.view_default, methods={'GET'})
        self.add_url_rule('/workbench', view_func=self.view_workbench, methods={'GET', 'POST'})
        # Open last env with config values
        # noinspection PyUnresolvedReferences,
        with path_env.open('r') as file:
            self.env_dh = json.load(file)  # type: dict
            assert isinstance(self.env_dh, dict)

        self.url_dh = "https://api.devicetag.io"

        # check if it has id
        url_info = '{}/desktop-app'.format(self.url_dh)
        if self.env_dh['id'] == "":
            snapshot_init = Workbench().run()
            self.new_config_response = requests.get(url=url_info, data=snapshot_init)
        else:
            self.new_config_response = requests.get(url=url_info)
        # self.env_dh = self.new_config_response.json()
        # Save new config in env file
        with Path(__file__).parent.joinpath('.env_dh.json').open('w') as file:
            json.dump(self.env_dh, file)

        self.workbench_queue = Queue()
        self.workbench_thread = WorkbenchThread(self.workbench_queue)
        self.workbench_thread.run()

        last_snapshot = parse(self.env_dh['lastSnapshot'])  # type: datetime
        days_between_snapshots = timedelta(days=self.env_dh['daysBetweenSnapshots'])

        # compare diff between dates and start wb process
        if (datetime.now() - last_snapshot) >= days_between_snapshots:
            self.workbench_queue.put(None)

    def view_workbench(self):
        """Execute workbench manually and returns snapshot to DH.
            Need to be root user
        """
        # POST put execution wb in queue
        if request.method == 'POST':
            self.workbench_queue.put(None)
            return Response(status=200)
        else:  # GET show json snapshot when finish wb process while 102 processing
            snapshot = self.workbench_thread.snapshot
            if snapshot is None:
                return Response(status=102)
            else:
                return jsonify(snapshot)

    def view_default(self):
        """Import template index.html"""
        return render_template('index.html', name='init')


class WorkbenchThread(Thread):
    def __init__(self, queue: Queue):
        super().__init__(daemon=True)
        self.env_dh = None
        self.workbench = Workbench()
        self.queue = queue
        self.snapshot = None
        self.url_dh = "https://api.devicetag.io"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def start(self):
        while True:
            self.queue.get()
            self.snapshot = None
            self.snapshot = self.workbench.run()
            self.upload_to_devicehub()

    def upload_to_devicehub(self):
        token = self.env_dh['token']

        headers_snapshot = self.headers
        headers_snapshot.update({'Authorization': token})
        db = self.env_dh['db']

        # POST Snapshot to Devicehub
        url_snapshot = '{}/{}/events/devices/snapshot'.format(self.url_dh, db)
        try:
            r = requests.post(url_snapshot, json=self.snapshot, headers=headers_snapshot)
            r.raise_for_status()
        except requests.HTTPError as e:
            print(e.response.content.decode())
