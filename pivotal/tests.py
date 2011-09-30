import unittest

from pivotal import Pivotal, BASE_URL, PROTO_SWITCH

class PivotalTest(unittest.TestCase):

    def test_protocol_switch(self):
        self.assertEqual(PROTO_SWITCH[True], 'https://')
        self.assertEqual(PROTO_SWITCH[False], 'http://')


    def _test_url_strings(self, use_https):
        pv = Pivotal('ABCDEF', use_https=use_https)

        url = PROTO_SWITCH[use_https] + BASE_URL
        
        self.assertEqual(pv.projects().url, url + 'projects')
        self.assertEqual(pv.projects(123).url, url + 'projects/123')
        self.assertEqual(pv.projects('123').url, url + 'projects/123')
        self.assertEqual(pv.projects('123').stories().url, 
                      url + 'projects/123/stories')
        self.assertEqual(pv.projects('123').stories(filter='state:unstarted').url,
                      url + 'projects/123/stories?filter=state%3Aunstarted')

        self.assertEqual(pv.projects('123').stories('456').tasks().url,
                url + 'projects/123/stories/456/tasks')
        self.assertEqual(pv.projects('123').stories('456').tasks('789').url,
                url + 'projects/123/stories/456/tasks/789')

    def test_https_urls(self):
        self._test_url_strings(use_https=True)

    def test_http_urls(self):
        self._test_url_strings(use_https=False)

    def test_update_url_strings(self):
        """
        Testing multiple `update` kwargs is may fail to do unordered
        dictionary keys
        """
        pv = Pivotal('ABCDEF', use_https=True)
        url = PROTO_SWITCH[True] + BASE_URL

        self.assertEqual(pv.projects('123').stories().add('story', name='New Story').url,
                url + 'projects/123/stories?story%5Bname%5D=New+Story')
        self.assertEqual(pv.projects('123').stories().update('story', name='New Story').url,
                url + 'projects/123/stories?story%5Bname%5D=New+Story')
        self.assertEqual(pv.projects('123').stories('456').update('story', name='Updated Story').url,
                url + 'projects/123/stories/456?story%5Bname%5D=Updated+Story')
        self.assertEqual(pv.projects('123').stories('456').tasks('789').update('task', description='count shields', priority=2, complete='false').url,
                url + 'projects/123/stories/456/tasks/789?task%5Bdescription%5D=count+shields&task%5Bcomplete%5D=false&task%5Bpriority%5D=2')
        


if __name__ == '__main__':
    unittest.main()
