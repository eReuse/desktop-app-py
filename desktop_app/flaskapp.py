from threading import Timer, Thread
from time import sleep

from ereuse_utils import ensure_utf8
from ereuse_workbench.workbench import Workbench
from flask import Flask, render_template, jsonify, json, request, Response
from multiprocessing import Process, Queue
from werkzeug.exceptions import NotFound
import sched


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
        self.workbench_queue = Queue()
        self.workbench_thread = WorkbenchThread(self.workbench_queue)
        self.workbench_thread.run()
        # todo get info from devicehub
        # if last event has been a while ago
        if last_event_while_ago:
            self.workbench_queue.put(None)


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

    def start(self):
        while True:
            self.queue.get()
            self.snapshot = self.workbench.run()
            # todo upload to devicehub




