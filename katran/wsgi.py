"""
WSGI config for katran project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

# -*- coding: utf-8 -*-

# import os,sys

# #путь к проекту
# sys.path.append('/home/k/katranpnev/dasein/public_html')
# #путь к фреймворку
# sys.path.append('/home/k/katranpnev/dasein')
# #путь к виртуальному окружению

# sys.path.append('/home/k/katranpnev/dasein/venv/lib/python3.11/site-packages/')
# #исключить системную директорию
# sys.path.remove('/usr/lib/python3.11/site-packages')
# from django.core.wsgi import get_wsgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'katran.settings')


# application = get_wsgi_application()

import os
import sys
sys.path.append('/home/k/katranpnev/dasein/public_html')
# sys.path.append('/home/k/katranpnev/dasein/default')
sys.path.append('/home/k/katranpnev/dasein')
sys.path.append('/home/k/katranpnev/dasein/venv/lib/python3.11/site-packages')

sys.path = [p for p in sys.path if not (p.startswith('/usr/lib/') and p.endswith('/site-packages'))]

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'katran.settings')

application = get_wsgi_application()