from django.http import HttpResponsePermanentRedirect


class WwwRedirectMiddleware:
    def __init__(self, get_response):  # ← это обязательно!
        self.get_response = get_response

    def __call__(self, request):
        # твоя логика здесь
        response = self.get_response(request)
        return response