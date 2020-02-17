from django.http import HttpResponseRedirect
from django.contrib.redirects.middleware import RedirectFallbackMiddleware


class TemporaryRedirectFallbackMiddleware(RedirectFallbackMiddleware):
    response_redirect_class = HttpResponseRedirect
