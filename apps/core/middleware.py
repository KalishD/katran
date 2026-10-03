from urllib.parse import urlunsplit

from django.http import HttpResponsePermanentRedirect


class WwwRedirectMiddleware:
    """Redirect the www host to the canonical host with a permanent redirect."""

    CANONICAL_HOST = 'katran-pnevmo.ru'
    REDIRECTED_HOSTS = frozenset({'www.' + CANONICAL_HOST})
    SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS'})

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().partition(':')[0]
        if host in self.REDIRECTED_HOSTS and request.method in self.SAFE_METHODS:
            target = urlunsplit((
                'https',
                self.CANONICAL_HOST,
                request.path,
                request.META.get('QUERY_STRING', ''),
                '',
            ))
            return HttpResponsePermanentRedirect(target)
        return self.get_response(request)


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
