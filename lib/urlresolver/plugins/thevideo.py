'''
thevideo urlresolver plugin
Copyright (C) 2014 Eldorado

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re, time, urllib
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 3

class TheVideoResolver(UrlResolver):
    name = "thevideo"
    domains = ["thevideo.me"]
    pattern = '(?://|\.)(thevideo\.me)/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.IE_USER_AGENT,
            'Referer': web_url
        }
        
        html = self.net.http_GET(web_url, headers=headers).content
        
        vt_url = re.search('(https://thevideo.me/jwjsv/[a-z0-9]*)', html)
        try: vt_url = vt_url.group(1)
        except: vt_url = 'https://thevideo.me/jwjsv/%s' % media_id
        
        vt_link = self.net.http_GET(vt_url, headers=headers).content
        vt = re.compile('\|([a-z0-9]*)\|').findall(vt_link)
        if not vt:
            raise ResolverError('Unable to locate link')
        try: vt = [i for i in vt if len(i) > 200][0]
        except: raise ResolverError('Unable to locate link')
        
        r = re.findall(r"'?label'?\s*:\s*'([^']+)p'\s*,\s*'?file'?\s*:\s*'([^']+)", html)
        if not r:
            raise ResolverError('Unable to locate link')
        else:
            max_quality = 0
            best_stream_url = None
            for quality, stream_url in r:
                if int(quality) >= max_quality:
                    best_stream_url = stream_url
                    max_quality = int(quality)
            if best_stream_url:
                return '%s%s%s' % (best_stream_url, '?direct=false&ua=1&vt=', vt)
            else:
                raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)
