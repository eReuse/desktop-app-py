#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys

# Set the working directory
sys.path.append('/opt/desktop-app')

from desktop_app.flaskapp import DesktopApp

if __name__ == "__main__":
    DesktopApp().run()