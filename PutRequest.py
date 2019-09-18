import urllib.request as req

class PutRequest(req.Request):
    '''class to handling putting with urllib2'''

    def __init__(self, *args, **kwargs):
        return req.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return 'PUT'