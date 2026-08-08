"""
WSGI config for katran project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

# -*- coding: utf-8 -*-

import os
import sys

# Путь к проекту (базовая директория проекта)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Путь к виртуальному окружению (если используется)
# Если используешь venv в папке env рядом с manage.py:
venv_path = os.path.join(BASE_DIR, 'env', 'lib', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'katran.settings')

application = get_wsgi_application()
