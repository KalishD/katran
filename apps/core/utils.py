import os
from io import BytesIO
from urllib.parse import urlparse
from django.core.files.base import ContentFile

def pil_to_django(image, format="JPEG"):
    fobject = BytesIO()
    # fobject = StringIO.StringIO()
    image.save(fobject, format=format)
    return ContentFile(fobject.getvalue())