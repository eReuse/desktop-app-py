import json
from multiprocessing import Queue
from threading import Thread

import requests
from ereuse_utils import ensure_utf8
from ereuse_workbench.workbench import Workbench
from flask import Flask, render_template, jsonify, request, Response
from werkzeug.exceptions import NotFound


class DesktopApp(Flask):
    """ todo Systemd root service desktop-app
        todo python scheduler per correr periodicament
        todo create icon.desktop
    """

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
        # with open('/path/to/.env_dh.json') as data:
        #    self.env_dh = json.load(data)
        #    print(self.env_dh)

        self.workbench_queue = Queue()
        self.workbench_thread = WorkbenchThread(self.workbench_queue)
        self.workbench_thread.run()
        # put REST vars Devicehub url,auth,
        # todo get info from devicehub
        # todo udpate env_dh.json with new info
        # if last event has been a while ago
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
        self.workbench = Workbench()
        self.queue = queue
        self.snapshot = None
        self.url_devicehub = "https://api.devicetag.io"
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
        # convert json to dict
        # snapshot_dict = json.loads(self.snapshot)

        # login devicehub
        # POST Login to get auth
        # data_login = config.mailDH + config.pwdDH
        data_login = {
            # todo get this values from env_dh_test.json
            "email": "desktop-app@ereuse.org",
            "password": 'XXX',
        }
        response = requests.post(self.url_devicehub, json=data_login, headers=self.headers)

        # todo get auth from response and push to headers
        # todo take defaultDatabase from response
        token = 'Basic ' + response.json()

        # in one line is possible?
        headers_snapshot = self.headers
        headers_snapshot.update({'Authorization': token})

        db = response.json()

        # upload snapshot
        # POST Snapshot to Devicehub
        url_snapshot = '{}/{}/events/devices/snapshot'.format(self.url_devicehub, db)
        try:
            r = requests.post(url_snapshot, json=self.snapshot, headers=headers_snapshot)
            r.raise_for_status()
        except requests.HTTPError as e:
            print(e.response.content.decode())
