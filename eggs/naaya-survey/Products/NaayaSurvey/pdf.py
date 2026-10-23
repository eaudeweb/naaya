"""HTML to PDF with WeasyPrint."""
from weasyprint import HTML
from weasyprint.urls import URLFetcher


class SiteURLFetcher(URLFetcher):
    """Fetch over HTTP, sending the user's cookies only to this site."""

    def __init__(self, request, **kwargs):
        super().__init__(timeout=10, **kwargs)
        self.site_url = request['SERVER_URL'] + '/'
        self.cookie = request.environ.get('HTTP_COOKIE', '')

    def fetch(self, url, headers=None):
        if self.cookie and url.startswith(self.site_url):
            headers = dict(headers or {}, Cookie=self.cookie)
        return super().fetch(url, headers)


def html_to_pdf(context, html):
    """PDF bytes of html rendered at context; images and CSS as the current user."""
    return HTML(string=html, base_url=context.absolute_url() + '/',
                url_fetcher=SiteURLFetcher(context.REQUEST)).write_pdf()
