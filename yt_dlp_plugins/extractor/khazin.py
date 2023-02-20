# ⚠ Don't use relative imports

# import q

import re
import urllib.error
import urllib.parse
import urllib.request
import html
import dateutil.parser
import isodate

from yt_dlp.extractor.common import InfoExtractor


# from yt_dlp.utils import (
# )

# ℹ️ If you need to import from another plugin
# from yt_dlp_plugins.extractor.example import ExamplePluginIE

# ℹ️ Instructions on making extractors can be found at:
# 🔗 https://github.com/yt-dlp/yt-dlp/blob/master/CONTRIBUTING.md#adding-support-for-a-new-site


# ⚠ The class name must end in "IE"
class KhazinIE(InfoExtractor):
    _WORKING = True
    _VALID_URL = r'^https://khazin.ru/'

    TITLE_RE = re.compile(
        r'\<title\>(?P<title>[^<]+?)(?: - khazin\.ru)?\</title\>', re.MULTILINE)

    IFRAME_RE = re.compile(
        r'<iframe[^>]+src=\"(?P<src>https://kinescope\.io/embed/(?P<embed_id>\S*))\"', re.MULTILINE)

    MASTER_STREAM_URL_RE = re.compile(
        r'(?P<s_url>https://kinescope\.io/(?P<id>\S+)/master\.m3u8)')

    def _real_extract(self, url):

        cls = KhazinIE

        self.to_screen('URL "%s" successfully captured' % url)
        rootWebpage = self._download_webpage(url, url, "Downloading root page")

        title = html.unescape(cls.TITLE_RE.search(rootWebpage).group('title'))

        m = cls.IFRAME_RE.search(rootWebpage)

        # q(rootWebpage)

        iframesrc = m.group('src')
        video_id = m.group('embed_id')

        req = urllib.request.Request(url=iframesrc, method='GET')
        req.add_header('referer', 'https://khazin.ru/')

        iframeWebpage = self._download_webpage(
            req, url, "Downloading kinescope media iframe")

        # q(iframeWebpage)

        m = cls.MASTER_STREAM_URL_RE.search(iframeWebpage)
        s_url = m.group('s_url')

        duration = None
        m = re.search(r'\"duration\": \"(?P<duration>\S+)\"', iframeWebpage)
        if m is not None:
            duration = isodate.parse_duration(m.group('duration')).seconds

        req = urllib.request.Request(url=s_url, method='GET')
        req.add_header('referer', 'https://khazin.ru/')

        formats = []
        formats.extend(self._extract_m3u8_formats(
            req, video_id))

        for f in formats:
            f['http_headers'] = {'Referer': 'https://khazin.ru/'}

        uploader = 'Михаил Хазин'

        published_time = int(dateutil.parser.parse(re.compile(
            r'<meta property=\"article:published_time\" content=\"(?P<published_time>\S+)\" />').search(rootWebpage).group('published_time')).timestamp())

        modified_time = None
        m = re.compile(
            r'<meta property=\"article:modified_time\" content=\"(?P<modified_time>\S+)\" />').search(rootWebpage)
        if m is not None:
            modified_time = int(dateutil.parser.parse(
                m.group('modified_time')).timestamp())

        result = {
            'id': video_id,
            'title': title,
            'formats': formats,
            'duration': duration,
            'timestamp': published_time,
            'modified_timestamp': modified_time,
            'uploader': uploader,
            'thumbnail': re.compile(r'<meta property=\"og:image\" content=\"(?P<image>\S+)\" />').search(rootWebpage).group('image'),
        }

        # q(result)

        return result
