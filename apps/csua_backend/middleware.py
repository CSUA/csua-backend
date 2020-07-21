from django.http import HttpResponseRedirect
from django.contrib.redirects.middleware import RedirectFallbackMiddleware


class TemporaryRedirectFallbackMiddleware(RedirectFallbackMiddleware):
    """
    This makes it so that django.contrib.redirects uses HTTP 307 rather than 301
    This way redirects can be changed--browsers won't cache them
    Read here:
    https://docs.djangoproject.com/en/3.0/ref/contrib/redirects/#middleware
    """

    response_redirect_class = HttpResponseRedirect
