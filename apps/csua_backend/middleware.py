from django.conf import settings
from django.contrib.redirects.middleware import RedirectFallbackMiddleware
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect


class TemporaryRedirectFallbackMiddleware(RedirectFallbackMiddleware):
    """
    This makes it so that django.contrib.redirects uses HTTP 307 Temporary
    Redirect rather than HTTP 301 Moved Permanently.
    This way redirects can be changed--browsers won't cache them.

    In contrast to the default RedirectFallbackMiddleware, we strip out the
    query parameters so that extraneous query parameters don't break redirects.

    E.g. GET /zoom/?fbclid=420 properly redirects using the redirect with old_path="/zoom/"

    Read here:
    https://docs.djangoproject.com/en/2.2/ref/contrib/redirects/#middleware

    """

    # from django/contrib/redirects/middleware.py
    def process_response(self, request, response):
        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        current_site = get_current_site(request)

        r = None
        try:
            r = Redirect.objects.get(site=current_site, old_path=request.path)
        except Redirect.DoesNotExist:
            pass
        if r is None and settings.APPEND_SLASH and not request.path.endswith("/"):
            try:
                r = Redirect.objects.get(site=current_site, old_path=request.path + "/")
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.new_path == "":
                return self.response_gone_class()
            return HttpResponseRedirect(r.new_path, status=307)

        # No redirect was found. Return the response.
        return response
