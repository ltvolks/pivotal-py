from anyetree import etree
import copy
import httplib2
from urllib import urlencode


BASE_URL = 'www.pivotaltracker.com/services/v3/'
PROTO_SWITCH = {
    True: 'https://',
    False: 'http://'
}

class Pivotal(object):

    def __init__(self, token, use_https=True):
        self.token = token
        self.path = []
        self.qs = {}
        self.use_https = bool(use_https)

    def __getattr__(self, method):
        # Create a new copy of self
        obj = self.__class__(self.token, self.use_https)
        obj.path = copy.copy(self.path)
        obj.qs = copy.copy(self.qs)
        
        obj.path.append(method)
        return obj.mock_attr

    def mock_attr(self, *args, **kwargs):
        """
        Empty method to call to slurp up args and kwargs.

        `args` get pushed onto the url path.
        `kwargs` are converted to a query string and appended to the URL.
        """
        self.path.extend(args)
        self.qs.update(kwargs)
        return self

    @property
    def url(self):
        url = PROTO_SWITCH[self.use_https] + BASE_URL + '/'.join(map(str, self.path))
        if self.qs:
            url += '?' + urlencode(self.qs)
        return url

    def get(self):
        h = httplib2.Http(timeout=15)
        h.force_exception_to_status_code = True
        headers = {
            'X-TrackerToken': self.token,
        }
        return h.request(self.url, headers=headers)

    def get_etree(self):
        response, content = self.get()
        return etree.fromstring(content)

    def post(self, body=None):
        """
        POST using url parameters

        # TODO: Support POST using body
        """
        h = httplib2.Http(timeout=15)
        h.force_exception_to_status_code = True
        headers = {
            'X-TrackerToken': self.token,
        }

        if body is None:
            return h.request(self.url, "POST", headers=headers)
        else:
            raise NotImplementedError

    def put(self, body=None):
        """
        PUT using url parameters
        Note: Content-Length must be set to 0 when using PUT with URL parameters
        
        # TODO: Support PUT using body
        """
        h = httplib2.Http(timeout=15)
        h.force_exception_to_status_code = True
        headers = {
            'X-TrackerToken': self.token,
        }

        if body is None:
            headers['Content-Length'] = '0'
            return h.request(self.url, "PUT", headers=headers)
        else:
            raise NotImplementedError

    def update(self, type, **kwargs):
        """
        Update querystring according using a subscript notation incorporating
        the `type` (story, task, label)
        Necessary to support POST and PUT using url parameters

        e.g.
        >>> story = pv.project(123).stories().update(type='story', name='New Story')
        >>> story.qs
        {'story[name]': 'New Story'}
        
        """
        subscripted = {}
        for k,v in kwargs.items():
            subscripted['%s[%s]' % (type, k)] = v
        self.qs.update(subscripted)
        return self
    add = update # Alias
