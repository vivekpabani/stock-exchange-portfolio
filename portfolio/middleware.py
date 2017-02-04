from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


class ExceptionMiddleware(object):
    """
    Show error messages in home page
    """

    def process_exception(self, request, exception):
        messages.warning(request, str(exception))

        return redirect(reverse("portfolios:home"))
