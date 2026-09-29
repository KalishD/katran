import mimetypes

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        # На этой платформе в mimetypes нет .webp, поэтому dev-сервер отдаёт
        # картинки как application/octet-stream. Браузеры такое терпят, но
        # строгие клиенты и CDN — нет. Регистрируем явно.
        mimetypes.add_type('image/webp', '.webp')

