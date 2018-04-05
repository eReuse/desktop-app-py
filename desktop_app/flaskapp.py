from ereuse_utils import ensure_utf8
from ereuse_workbench.workbench import Workbench
from flask import Flask, render_template, jsonify
from werkzeug.exceptions import NotFound
"""import sched"""


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
        self.workbench = Workbench()
        self.add_url_rule('/', view_func=self.view_default, methods={'GET'})
        self.add_url_rule('/info', view_func=self.view_info, methods={'GET'})
        # self.add_url_rule('/workbench', view_func=self.view_workbench, methods={'POST'})

    def view_info(self):
        raise NotFound()

    def execute_workbench(self):
        """Execute workbench manually and returns the result.
            Need to be root user
        """
        snapshot = self.workbench.run()
        return jsonify(snapshot)

    def view_default(self):
        """Import template index.html"""
        return render_template('index.html', name='init')
