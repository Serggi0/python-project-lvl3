response_codes = {
    100: 'Continue.',
    101: 'Switching Protocol',
    102: 'Processing',
    103: 'Early Hints',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    300: 'Redirection',
    301: 'Redirection',
    302: 'Redirection',
    303: 'Redirection',
    304: 'Redirection',
    305: 'Redirection',
    306: 'Redirection',
    307: 'Redirection',
    400: 'Bad Request. Server does not understand the request'
         ' due to invalid syntax',
    401: 'Unauthorized',
    403: 'Forbidden. The client does not have access rights to the content,'
         ' so the server refuses to give a proper response',
    404: 'Not Found. The server cannot find the requested resource.',
    405: 'Method Not Allowed. Server knows about the requested method,'
         ' but it has been deactivated and cannot be used.',
    406: 'Not Acceptable. Server did not find any content.',
    408: 'Request Timeout. The 408 (Request Timeout) status code indicates'
         ' that the server did not receive a complete request message'
         ' within the time that it was prepared to wait.',
    409: 'Conflict. The request could not be completed'
         ' due to a conflict with the current state of the target resource.',
    410: 'Gone. The requested content has been deleted from the server.',
    411: 'Length Required',
    412: 'Precondition Failed.The client has specified in its headers'
         ' the conditions that the server cannot fulfill',
    500: 'Internal Server Error. The server is faced with a situation'
         ' that it does not know how to handle.',
    501: 'Not Implemented. The request method is not supported by the server'
         ' and cannot be processed.',
    502: 'Bad Gateway. Server, while working as a gateway to receive'
         ' the response needed to process the request,'
         ' received an invalid (invalid) response.',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported'

}
