from ereuse_utils import ensure_utf8
from flask import Flask
from werkzeug.exceptions import NotFound


class DesktopApp(Flask):
    def __init__(self, import_name=__name__, static_path=None, static_url_path=None,
                 static_folder='static', template_folder='templates', instance_path=None,
                 instance_relative_config=False, root_path=None):
        ensure_utf8(self.__class__.__name__)
        super().__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                         instance_path, instance_relative_config, root_path)
        self.add_url_rule('/info', view_func=self.view_info, methods={'GET'})
        self.add_url_rule('/workbench', view_func=self.view_workbench, methods={'POST'})

    def view_info(self):
        raise NotFound()

    def view_workbench(self):
        """Execute workbench and returns the result."""
