from .comparison import Comparison


def comparison(request):
    return {'comparison': Comparison(request)}
