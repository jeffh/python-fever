from urllib2 import urlopen
from urllib import urlencode
from datetime import datetime
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

try:
    import json
except ImportError:
    import simplejson as json
    
__all__ = ['UnsupportedAPI', 'FeverAPI']
    
def post_url(url, data):
    handle = None
    content = None
    try:
        handle = urlopen(url, urlencode(data))
        content = handle.read()
        if content:
            encoding = handle.headers['content-type'].split('charset=')[-1]
            content = unicode(content, encoding)
    finally:
        if handle is not None:
            handle.close()
    return content

class UnsupportedAPI(Exception):
    def __init__(self, feature, requires_version):
        super(UnsupportedAPI, self).__init__(
            "%s is not supported in Fever's API version < %d" % (
                feature, requires_version))

class FeverAPIFavicon(dict):
    def __init__(self, *args, **kwargs):
        super(FeverAPIFavicon, self).__init__(*args, **kwargs)
        index = self['data'].find(';')
        assert index >= 0
        self['type'] = self['data'][:index]
        index = self['data'].find(',')
        assert index >= 0
        self['raw_data'] = self['data'][index+1:]

class FeverAPI(object):
    """
    The public API for interacting with a feed-a-fever installation.
    
    To connect, you must first authenticate:
    
    >>> fever = FeverAPI("http://mydomain.com/fever/")
    >>> fever.authenticate("myusername", "mypassword")
    
    See http://feedafever.com/api for information reguarding the return
    values. All return values are in a dictionary form.
    """
    def __init__(self, url):
        self.url = url
        self.api_key = None
        self.api_version = None
        
    @property
    def auth_url(self):
        """Used internally.
        The URL used the access the API and used to check authentication.
        """
        return self.url + '?api'
    
    @property
    def groups_url(self):
        "Used Internally. The URL used to access fever groups."
        return self.auth_url + '&groups'
    
    @property
    def feeds_url(self):
        "Used Internally. The URL used to access fever feeds."
        return self.auth_url + '&feeds'
    
    @property
    def favicons_url(self):
        "Used Internally. The URL used to access fever favicons."
        return self.auth_url + '&favicons'
    
    @property
    def items_url(self):
        "Used Internally. The URL used to access fever feed items."
        return self.auth_url + '&items'
    
    @property
    def hotlinks_url(self):
        "Used Internally. The URL used to access fever hotlinks."
        return self.auth_url + '&links'
    
    @property
    def unread_items_url(self):
        "Used Internally. The URL used to access unread feed items."
        return self.auth_url + '&unread_item_ids'
    
    @property
    def saved_items_urls(self):
        "Used Internally. The URL used to access saved fever feed items."
        return self.auth_url + '&saved_item_ids'
    
    @property
    def is_authenticated(self):
        "Returns True if we are logged in to a given site."
        return self.api_key is not None
    
    def post_url(self, url=None, dic=None):
        """Used internally. Not recommended to invoke manually.
        
        Performs a POST request to the given URL with dic as post-data.
        Automatically inserts the api_key and expects JSON returned.
        
        Also converts last_refreshed_on_time to a python datetime.
        """
        if url is None:
            url = self.auth_url
        if dic is None:
            dic = {}
        dic.update({'api_key': self.api_key})
        result = json.loads(post_url(url, dic))
        if 'last_refreshed_on_time' in result:
            result['last_refreshed_on_time'] = datetime.fromtimestamp(int(result['last_refreshed_on_time']))
        return result
        
    def authenticate(self, username, password=None):
        """Authenticates with the remote fever site.
        
        You must call this before using any other API calls.
        
        Leaving the password parameter blank will prompt via console.
        """
        hash = md5()
        hash.update(username)
        hash.update(':')
        if password is not None:
            hash.update(password)
        else:
            import getpass
            hash.update(getpass.getpass('Password: '))
        self.api_key = hash.hexdigest()
        
        response = self.post_url() # defaults => auth
        self.api_version = response['api_version']
        if not response['auth']:
            self.api_key = None
        return response
        
    def get(self, url, data=None):
        """Used internally. Not recommended to invoke manually.
        
        identical to self.post_url(), except checks for an authenticate()
        call before invoking.
        """
        assert self.api_key, "You must invoke authenticate first."
        if data:
            data = urlencode(data)
        else:
            data = ""
        return self.post_url("%s&%s" % (url, data))

    def get_groups(self):
        """Returns a dictionary of the response to fetching all the fever groups.
        
        An example return::
            {
                "api_version": 2,
                "auth": 1,
                "last_refreshed_on_time": datetime.datetime(2010, 12, 24, 14, 47, 23),
                "groups": [
                    {"id":10, "title":"Publications"},
                    {"id":2,  "title":"Personal"}
                    //...
                ]
            }
        
        """
        return self.get(self.groups_url)
    
    def get_feeds(self):
        """Returns a dictionary of the response to fetching all the feeds.
        
        An example return::
            {
                "api_version": 2,
                "auth": 1,
                "last_refreshed_on_time": datetime.datetime(2010, 12, 24, 14, 47, 23),
                "feeds": [
                    {
                        'last_updated_on_time': 1296866558,
                        'title': 'I Will Teach You To Be Rich',
                        'url': 'http://www.iwillteachyoutoberich.com/feed/',
                        'site_url': 'http://www.iwillteachyoutoberich.com',
                        'is_spark': 0,
                        'favicon_id': 2,
                        'id': 1
                    },
                    {
                        'last_updated_on_time': 1288623542,
                        'title': 'I am Paddy',
                        'url': 'http://feeds2.feedburner.com/iampaddy',
                        'site_url': 'http://blog.iampaddy.com',
                        'is_spark': 0,
                        'favicon_id': 3,
                        'id': 2
                    },
                    //...
                ],
                "feeds_groups": [
                    {'group_id': 15, 'feed_ids': '1,127'},
                    {'group_id': 4, 'feed_ids': '2,23,25,40,57,74,76,77,120,121'},
                    {'group_id': 16, 'feed_ids': '3,11,121,130,135'}
                    // ...
                ]
            }
        
        """
        results = self.get(self.feeds_url)
        for feed in results['feeds']:
            feed['feed_ids'] = tuple(map(int, link['feed_ids'].split(',')))
        return results
    
    def get_favicons(self):
        """Returns a dictionary of the response to fetching all the favicons.
        
        An example return::
            {
                "api_version": 2,
                "auth": 1,
                "last_refreshed_on_time": datetime.datetime(2010, 12, 24, 14, 47, 23),
                "favicons": [
                    {
                        'type': 'image/gif',
                        'data': 'image/gif;base64,R0lGODlhAQABAIAAAObm5gAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==',
                        'id': 1,
                        'raw_data': 'R0lGODlhAQABAIAAAObm5gAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
                    },
                    {
                        'type': 'image/png',
                        'data': 'image/png;base64,...',
                        'id': 2,
                        'raw_data': '..'
                    }
                
                ]
            }
        """
        result = self.get(self.favicons_url)
        result['favicons'] = tuple([FeverAPIFavicon(x) for x in result['favicons']])
        return result
    
    def get_items(self, since_id=None, max_id=None, with_id=None):
        """Returns a dictionary of the response to fetching items.
        Due to the restriction of the API, you'll only get 50 items at the max.
        
        An example return::
            {
                "api_version": 2,
                "auth": 1,
                "last_refreshed_on_time": datetime.datetime(2010, 12, 24, 14, 47, 23),
                "total_items": '39606',
                "items": [
                    {
                        'created_on_time': 1269843910,
                        'author': '',
                        'url': 'http://pulsewave.willhui.net/post/481107479',
                        'title': 'The disadvantages of an elite education',
                        'html': '<a href="http://www.theamericanscholar.org/the-disadvantages-of-an-elite-education/">The disadvantages of an elite education</a>: <p>Also from theamericanscholar.org.</p>',
                        'is_read': 1,
                        'feed_id': 46,
                        'is_saved': 1,
                        'id': 22590
                    },
                    {
                        'created_on_time': 1270568044,
                        'author': 'Aza Raskin',
                        'url': 'http://www.azarask.in/blog/post/the-seduction-of-simple-hidden-complexity/',
                        'title': 'The Seduction of Simple: Hidden Complexity',
                        'html': '<p>....</p>',
                        'is_read': 1,
                        'feed_id': 32,
                        'is_saved': 1,
                        'id': 34331
                    }
                ]
            }
        """
        if self.api_version < 2 and with_id is not None:
            raise UnsupportedAPI("get_items' with_ids parameter", requires_version=2)
        
        options = {}
        if since_id is not None:
            options['since_id'] = since_id
        if max_id is not None:
            options['max_id'] = max_id
        if with_id is not None:
            options['with_id'] = with_id
        
        return self.get(self.items_url, options)
    
    def get_hotlinks(self, offset=None, range=None):
        """Returns a dictionary of hotlinks.
        
        An example return::
            {
                "api_version": 2,
                "auth": 1,
                "last_refreshed_on_time": datetime.datetime(2010, 12, 24, 14, 47, 23),
                "use_celsius": 0,
                "items": [
                    {
                        'is_local': 0,
                        'is_item': 1,
                        'item_ids': (252774, 252637, 252082, 252050, 251972, 251267, 250621, 250524, 250400, 250387, 250247, 250237, 250147),
                        'title': 'Google: Bing Is Cheating, Copying Our Search Results',
                        'url': 'http://searchengineland.com/google-bing-is-cheating-copying-our-search-results-62914',
                        'feed_id': 44,
                        'is_saved': 0,
                        'item_id': 250147,
                        'id': 5715446,
                        'temperature': 108.6
                    },
                    {
                        'is_local': 1,
                        'is_item': 1,
                        'item_ids': (252637, 251972, 250823, 250657, 250621, 250575, 250672, 250826, 250524),
                        'title': 'Microsoft\u2019s Bing uses Google search results\u2014and denies it',
                        'url': 'http://googleblog.blogspot.com/2011/02/microsofts-bing-uses-google-search.html',
                        'feed_id': 54,
                        'is_saved': 0,
                        'item_id': 250524,
                        'id': 5724943,
                        'temperature': 107.4
                    }
                    // ...
                ]
            }
        """
        url = self.hotlinks_url
        if offset is not None:
            url += '&offset=%d' % offset
        if range is not None:
            url += '&range=%d' % range
        result = self.get(self.hotlinks_url)
        for link in result['links']:
            link['item_ids'] = tuple(map(int, link['item_ids'].split(',')))
        return result
        
