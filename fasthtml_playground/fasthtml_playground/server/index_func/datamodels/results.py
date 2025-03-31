from typing import Generic, Optional, TypeVar

T = TypeVar("T")
Output = TypeVar("OutT")


class Result(Generic[T]):
    """
    Base result class. Not intended to be used directly.
    """

    def __init__(self, data: T):
        self.success = False
        self.value: Optional[T] = None


class SuccessResult(Result[T]):
    """
    Result of a successfull operation. Contains the value returned by the operation.
    """

    def __init__(self, value: Optional[T]):
        super().__init__(value)
        self.success = True
        self.value = value


class CleanIndexCreateResult(SuccessResult):
    """
    Result of a successfull index create. Contains the value returned by the operation.
    """

    def __init__(self, value: Optional[T]):
        super().__init__(value)
        self.success = True
        self.value = value


class OverwriteIndexCreateResult(SuccessResult):
    """
    Result of a successfull index create with no overwrite.
    """

    def __init__(self, value: Optional[T]):
        super().__init__(value=value)


class IndexExistsResult(SuccessResult):
    """
    Result of a successfull index create because index exists
    """

    def __init__(self, value: Optional[T]):
        super().__init__(value=value)


class ErrorResult(Result[T]):
    """
    Result of an errorfull operation. Contains the error message.
    """

    def __init__(self, message: str):
        super().__init__(value=None)
        self.success = False
        self.message = message
