class AppInternalError(Exception):
    pass


class BadRequest(AppInternalError):
    pass


class BadPath(AppInternalError):
    pass


class BadFile(AppInternalError):
    pass
