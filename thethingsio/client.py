import json
import sys
import urllib2

class Client(object):
    def __init__(self, endpoint='https://api.thethings.io/v2'):
        self._endpoint = endpoint

    def _request(self, method, path, payload=None, headers=None, stream=None, timeout=10):

        # Parse object to JSON string
        if payload is not None and not isinstance(payload, basestring):
            payload = json.dumps(payload)

        url = path if path.startswith('http') else self._endpoint + path

        default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'thethings.iO Api Client/%s (Python %s)' % ('0.1', '.'.join(map(str,sys.version_info)))
        }

        req = urllib2.Request(url, payload, default_headers)
        req.get_method = lambda: method.upper()

        if headers is not None:
            for key, value in headers.iteritems():
                req.add_header(key, value)

        try:
            return Response(urllib2.urlopen(req, timeout=timeout), stream=stream)
        except urllib2.HTTPError, e:
            raise ApiError(e)

    def subscribe(self, path, headers=None, timeout=60):
        return self._request('GET', path + '?keepAlive=' + str(timeout * 1000), headers, stream=True, timeout=timeout)

    def get(self, path, headers=None):
        return self._request('GET', path, None, headers)

    def delete(self, path, headers=None):
        return self._request('DELETE', path, None, headers)

    def post(self, path, payload=None, headers=None):
        return self._request('POST', path, payload, headers)

    def put(self, path, payload=None, headers=None):
        return self._request('PUT', path, payload, headers)

    def patch(self, path, payload=None, headers=None):
        return self._request('PATCH', path, payload, headers)


class Response(object):
    def __init__(self, response, stream=None):
        self._stream = response.headers.get('transfer-encoding', None) == 'chunked'
        self._meta = response.headers

        if stream is True and not self._stream:
            raise ApiError('Invalid streaming HTTP response.')

        if (self._stream):
            iter = Response._iter_chunks(response)
            self._data = iter.next()
            self._iter = iter
        else:
            self._data = json.load(response)

        if (self.data[u'status'] == u'error'):
            raise ApiError(self.data[u'message'])

    def __str__(self):
        return str(self._data)

    @property
    def data(self):
        return self._data

    @property
    def stream(self):
        if not self._stream:
            raise Exception("Not a streaming response")
        return self._iter

    @property
    def contentType(self):
        return self._meta['Content-Type']

    @staticmethod
    def _iter_chunks(res):
        delims = 0
        buf = ''
        while True:
            chunk = res.read(1)

            if chunk in ('[', '{'): delims += 1
            elif chunk in (']', '}'): delims -= 1

            buf += chunk
            if (len(buf) > 0 and delims == 0):
                yield json.loads(buf)
                buf = ''

class ApiError(Exception):
    def __init__(self, message, *args, **kwargs):
        if isinstance(message, urllib2.HTTPError):
            try:
                data = json.load(message)
                if (data[u'status'] == u'error' and u'message' in data):
                    message = '(Error %d) ' % message.code + data[u'message']
            except Exception, e:
                pass
        super(ApiError, self).__init__(message, *args)
