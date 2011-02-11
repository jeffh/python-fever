import unittest
from fever import fever # patch works on the origin, not a proxy source
import os
from describe import Value
from mock import patch

class FeverTestCase(unittest.TestCase):
    def setUp(self):
        self.url = 'http://localhost/fever/'
        self.f = fever.FeverAPI(self.url)
        
    def load_fixture(self, file):
        f = None
        contents = ""
        try:
            f = open(os.path.join(os.path.dirname(__file__), file))
            contents = f.read()
        finally:
            if f is not None:
                f.close()
        return contents

class AuthenticatedFeverTestCase(FeverTestCase):
    def setUp(self):
        super(AuthenticatedFeverTestCase, self).setUp()
        self.f.api_key = 'lol'
        self.f.api_version = 2

class TestFeverAuthentication(FeverTestCase):
    @patch.object(fever, 'post_url')
    def test_successful_authenticate(self, read):
        read.return_value = '{"api_version":2,"auth":1,"last_refreshed_on_time":"1293217202"}'
        
        val = Value(self.f.authenticate(username='foo', password='bar'))
        val.get['auth'].should.be.true()
        
        api_key = '4e99e8c12de7e01535248d2bac85e732'
        Value(self.f.api_key).should == api_key
        read.assert_called_with(self.url+'?api', {'api_key': api_key})
        Value(self.f.is_authenticated).should.be.true()
    
    @patch.object(fever, 'post_url')
    def test_failed_authenticate(self, read):
        read.return_value = '{"api_version":2,"auth":0}'
        
        val = Value(self.f.authenticate(username='foo', password='bar'))
        val.get['auth'].should.be.false()
        
        Value(self.f.is_authenticated).should.be.false()

class TestFeverGroups(AuthenticatedFeverTestCase):
    @patch.object(fever, 'post_url')
    def test_get_groups(self, read):
        read.return_value = self.load_fixture('get_groups.json')
        
        val = Value(self.f.get_groups())
        val.get['groups'].should.have(12).items
        val.get['feeds_groups'].should.have(12).items

class TestFeverFeeds(AuthenticatedFeverTestCase):
    @patch.object(fever, 'post_url')
    def test_get_feeds(self, read):
        read.return_value = self.load_fixture('get_feeds.json')
        
        val = Value(self.f.get_feeds())
        val.get['feeds'].should.have(126).items
        val.get['feeds_groups'].should.have(12).items

class TestFeverFavicons(AuthenticatedFeverTestCase):
    @patch.object(fever, 'post_url')
    def test_get_favicons(self, read):
        read.return_value = self.load_fixture('get_favicons.json')
        
        val = Value(self.f.get_favicons())
        val.get['favicons'].should.have(99).items
        
        item = val['favicons'][0]
        item['data'].should.be.true()
        item['type'].should == "image/gif"
        item['raw_data'].should == 'R0lGODlhAQABAIAAAObm5gAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
        
class TestFeverHotLinks(AuthenticatedFeverTestCase):
    @patch.object(fever, 'post_url')
    def test_get_hotlinks(self, read):
        read.return_value = self.load_fixture('get_hotlinks.json')
        
        val = Value(self.f.get_hotlinks())
        val.get['links'].should.have(20).items
        
        item = val['links'][0]
        item['item_ids'].should.have(8).items
        item['item_ids'][0].should.be.type_of(int)

class TestFeverSync(AuthenticatedFeverTestCase):
    @patch.object(fever, 'post_url')
    def test_get_sync(self, read):
        read.return_value = self.load_fixture