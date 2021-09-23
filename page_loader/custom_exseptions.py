class AppInternalError(Exception):
    pass


class BadConnect(AppInternalError):
    pass


class ErrorSistem(AppInternalError):
    pass
