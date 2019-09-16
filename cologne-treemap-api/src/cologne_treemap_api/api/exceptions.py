from typing import Any

from jsonrpc.exceptions import JSONRPCDispatchException


class InternalError(JSONRPCDispatchException):
    """Error indicating that something went wrong internally."""

    def __init__(self, message: str, data: Any = None) -> None:
        super(InternalError, self).__init__(code=1, data=data, message=message)


class InvalidRequest(JSONRPCDispatchException):
    """Error indicating that the supplied parameters are wrong."""

    def __init__(self, message: str, data: Any = None) -> None:
        super(InvalidRequest, self).__init__(code=2, data=data, message=message)
