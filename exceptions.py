class NPRError(Exception):
    pass

class DetectorError(NPRError):
    pass

class InvalidSourceError(DetectorError):
    pass