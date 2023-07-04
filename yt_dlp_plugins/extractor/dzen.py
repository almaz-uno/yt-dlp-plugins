import re
from yt_dlp.utils import (
    determine_ext,
    extract_attributes,
    int_or_none,
    try_get,
)


from yt_dlp.extractor.common import InfoExtractor

class ZenYandexIE(InfoExtractor):
    _VALID_URL = r'https?://(zen\.yandex|dzen)\.ru(?:/video)?/(media|watch)/(?:(?:id/[^/]+/|[^/]+/)(?:[a-z0-9-]+)-)?(?P<id>[a-z0-9-]+)'
    _TESTS = [{
        'url': 'https://zen.yandex.ru/media/id/606fd806cc13cb3c58c05cf5/vot-eto-focus-dedy-morozy-na-gidrociklah-60c7c443da18892ebfe85ed7',
        'info_dict': {
            'id': '60c7c443da18892ebfe85ed7',
            'ext': 'mp4',
            'title': 'ВОТ ЭТО Focus. Деды Морозы на гидроциклах',
            'description': 'md5:f3db3d995763b9bbb7b56d4ccdedea89',
            'thumbnail': 're:^https://avatars.dzeninfra.ru/',
            'uploader': 'AcademeG DailyStream'
        },
        'params': {
            'skip_download': 'm3u8',
            'format': 'bestvideo',
        },
        'skip': 'The page does not exist',
    }, {
        'url': 'https://dzen.ru/media/id/606fd806cc13cb3c58c05cf5/vot-eto-focus-dedy-morozy-na-gidrociklah-60c7c443da18892ebfe85ed7',
        'info_dict': {
            'id': '60c7c443da18892ebfe85ed7',
            'ext': 'mp4',
            'title': 'ВОТ ЭТО Focus. Деды Морозы на гидроциклах',
            'description': 'md5:f3db3d995763b9bbb7b56d4ccdedea89',
            'thumbnail': r're:^https://avatars\.dzeninfra\.ru/',
            'uploader': 'AcademeG DailyStream',
            'upload_date': '20191111',
            'timestamp': 1573465585,
        },
        'params': {'skip_download': 'm3u8'},
    }, {
        'url': 'https://zen.yandex.ru/video/watch/6002240ff8b1af50bb2da5e3',
        'info_dict': {
            'id': '6002240ff8b1af50bb2da5e3',
            'ext': 'mp4',
            'title': 'Извержение вулкана из спичек: зрелищный опыт',
            'description': 'md5:053ad3c61b5596d510c9a199dc8ee633',
            'thumbnail': r're:^https://avatars\.dzeninfra\.ru/',
            'uploader': 'TechInsider',
            'timestamp': 1611378221,
            'upload_date': '20210123',
        },
        'params': {'skip_download': 'm3u8'},
    }, {
        'url': 'https://dzen.ru/video/watch/6002240ff8b1af50bb2da5e3',
        'info_dict': {
            'id': '6002240ff8b1af50bb2da5e3',
            'ext': 'mp4',
            'title': 'Извержение вулкана из спичек: зрелищный опыт',
            'description': 'md5:053ad3c61b5596d510c9a199dc8ee633',
            'thumbnail': 're:^https://avatars.dzeninfra.ru/',
            'uploader': 'TechInsider',
            'upload_date': '20210123',
            'timestamp': 1611378221,
        },
        'params': {'skip_download': 'm3u8'},
    }, {
        'url': 'https://zen.yandex.ru/media/id/606fd806cc13cb3c58c05cf5/novyi-samsung-fold-3-moskvich-barahlit-612f93b7f8d48e7e945792a2?from=channel&rid=2286618386.482.1630817595976.42360',
        'only_matching': True,
    }, {
        'url': 'https://dzen.ru/media/id/606fd806cc13cb3c58c05cf5/novyi-samsung-fold-3-moskvich-barahlit-612f93b7f8d48e7e945792a2?from=channel&rid=2286618386.482.1630817595976.42360',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        redirect = self._search_json(r'var it\s*=', webpage, 'redirect', id, default={}).get('retpath')
        if redirect:
            video_id = self._match_id(redirect)
            webpage = self._download_webpage(redirect, video_id, note='Redirecting')
        data_json = self._search_json(
            r'data\s*=', webpage, 'metadata', video_id, contains_pattern=r'{["\']_*serverState_*video.+}')
        serverstate = self._search_regex(r'(_+serverState_+video-site_[^_]+_+)',
                                         webpage, 'server state').replace('State', 'Settings')
        uploader = self._search_regex(r'(<a\s*class=["\']card-channel-link[^"\']+["\'][^>]+>)',
                                      webpage, 'uploader', default='<a>')

        duration = None
        m = re.search(r'<meta property=\"video:duration\" content=\"(?P<duration>\d+)\">', webpage)
        # m = re.search(r'\"duration\": \"(?P<duration>\S+)\"', webpage)
        if m is not None:
            duration = int(m.group('duration'))


        uploader_name = extract_attributes(uploader).get('aria-label')
        video_json = try_get(data_json, lambda x: x[serverstate]['exportData']['video'], dict)
        stream_urls = try_get(video_json, lambda x: x['video']['streams'])
        formats = []
        for s_url in stream_urls:
            ext = determine_ext(s_url)
            if ext == 'mpd':
                formats.extend(self._extract_mpd_formats(s_url, video_id, mpd_id='dash'))
            elif ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(s_url, video_id, 'mp4'))
        return {
            'id': video_id,
            'title': video_json.get('title') or self._og_search_title(webpage),
            'formats': formats,
            'duration': duration,
            'view_count': int_or_none(video_json.get('views')),
            'timestamp': int_or_none(video_json.get('publicationDate')),
            'uploader': uploader_name or data_json.get('authorName') or try_get(data_json, lambda x: x['publisher']['name']),
            'description': self._og_search_description(webpage) or try_get(data_json, lambda x: x['og']['description']),
            'thumbnail': self._og_search_thumbnail(webpage) or try_get(data_json, lambda x: x['og']['imageUrl']),
        }
