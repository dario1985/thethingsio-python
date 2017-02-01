import Queue
import threading
import warnings

from datetime import datetime

from thethingsio import Client


class ThingWriter(object):
    def __init__(self, thing_token, options=None, client=None):
        self._client = Client() if client is None else client
        self._thing_token = thing_token
        self._values = []
        self._chunk_size = 100

        if not isinstance(self._client, Client):
            raise TypeError('client expected to be a instanceof thethingsio.Client')

    def add(self, name, value=None, geo=None, date_time=None, ttl=None):
        value = {
            u'key': name,
            u'value': value,
            u'datetime': datetime.now().isoformat() if date_time is None else date_time
        }

        if geo is not None:
            if not isinstance(geo, (dict, tuple)):
                raise TypeError('Expected a tuple(long, lat) or a dict {lat, long} object')
            if isinstance(geo, tuple):
                geo = {'long': float(geo[0]), 'lat': float(geo[1])}
            elif not ('long' in geo and 'lat' in geo):
                raise TypeError('Expected a dict with valid lat, long values')
            value[u'geo'] = geo

        self._values.append(value)

    def __len__(self):
        return len(self._values)

    def flush(self, chunk_size=None):
        chunk_size = self._chunk_size if chunk_size is None else chunk_size
        if chunk_size > 1000:
            warnings.warn("Excessive batch size %d")

        chunks = [self._values[x:x + chunk_size] for x in xrange(0, len(self._values), chunk_size)]
        del self._values[:]

        def _write(client, token, values, failed):
            try:
                client.post('/things/' + token, {'values': values})
            except Exception as error:
                failed.put((error, values))

        errors = Queue.Queue()
        threads = [threading.Thread(target=_write, args=(self._client, self._thing_token, values, errors)) for values in
                   chunks]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if not errors.empty():
            reason = None
            for elem in list(errors.queue):
                reason, values = elem
                self._values += values
            raise Exception('Some values cannot be flushed to server due to an error: ' + str(reason))
