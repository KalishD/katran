from django.http import HttpResponsePermanentRedirect


class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class CacheControlMiddleware:
    """Set Cache-Control headers for static and media files."""

    STATIC_MAX_AGE = 60 * 60 * 24 * 30  # 30 days
    MEDIA_MAX_AGE = 60 * 60 * 24 * 7   # 7 days

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path
        if path.startswith('/static/'):
            response['Cache-Control'] = f'public, max-age={self.STATIC_MAX_AGE}, immutable'
        elif path.startswith('/media/'):
            response['Cache-Control'] = f'public, max-age={self.MEDIA_MAX_AGE}'

        return response
