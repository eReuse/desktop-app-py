import json
from multiprocessing import Queue
from pathlib import Path
from threading import Thread

import requests
import flask_cors
from ereuse_utils import ensure_utf8, DeviceHubJSONEncoder
from ereuse_workbench.workbench import Workbench
from flask import Flask, render_template, jsonify, request, Response
from werkzeug.exceptions import NotFound
from ereuse_utils.test import Client


class DesktopApp(Flask):
    """ todo Systemd root service desktop-app
        todo python scheduler per correr periodicament
        todo create icon.desktop
    """

    test_client_class = Client
    json_encoder = DeviceHubJSONEncoder

    def __init__(self, import_name=__name__, static_path=None, static_url_path=None,
                 static_folder='static', template_folder='templates', instance_path=None,
                 instance_relative_config=False, root_path=None):
        ensure_utf8(self.__class__.__name__)
        super().__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                         instance_path, instance_relative_config, root_path)
        self.add_url_rule('/', view_func=self.view_default, methods={'GET'})
        self.add_url_rule('/info', view_func=self.view_info, methods={'GET'})
        self.add_url_rule('/workbench', view_func=self.view_workbench, methods={'GET', 'POST'})
        # todo load env with config values
        # noinspection PyUnresolvedReferences
        with Path(__file__).parent.joinpath('.env_dh.json').open('r') as file:
            self.env_dh = json.load(file)  # type: dict
            assert isinstance(self.env_dh, dict)

        # todo get info_config from devicehub
        # todo udpate env_dh.json with new config
        self.url_dh = "https://api.devicetag.io"

        # todo if not id in self.config then run wb and get/post snapshot
        url_info = '{}/desktop-app'.format(self.url_dh)
        if self.env_dh['id'] == "":
            snapshot_init = Workbench().run()
            self.new_config_response = requests.get(url=url_info, data=snapshot_init)
        else:
            self.new_config_response = requests.get(url=url_info)
        self.env_dh = self.new_config_response.json()
        with Path(__file__).parent.joinpath('.env_dh.json').open('w') as file:
            json.dump(self.config, file)

        self.workbench_queue = Queue()
        self.workbench_thread = WorkbenchThread(self.workbench_queue)
        self.workbench_thread.run()

        # if last event has been a while ago
        # take local date and compare with config.lastWorkbench
        # if last_event_while_ago:
        #  self.workbench_queue.put(None)

    def view_info(self):
        raise NotFound()

    def view_workbench(self):
        """Execute workbench manually and returns the result.
            Need to be root user
        """
        if request.method == 'POST':
            self.workbench_queue.put(None)
            return Response(status=200)
        else:  # GET
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
            self.snapshot = self.workbench.run()
            # if workbench is finish:
            # todo upload to devicehub
            #   self.upload_to_devicehub()

    def upload_to_devicehub(self):

        # todo get to DH update env_dh
        # todo take defaultDatabase from response
        token = self.env_dh.get('token')

        headers_snapshot = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        headers_snapshot.update({'Authorization': token})
        db = self.env_dh.get

        # upload snapshot
        # POST Snapshot to Devicehub
        url_snapshot = '{}/{}/events/devices/snapshot'.format(self.url_dh, db)
        try:
            r = requests.post(url_snapshot, json=self.snapshot, headers=headers_snapshot)
            r.raise_for_status()
        except requests.HTTPError as e:
            print(e.response.content.decode())
