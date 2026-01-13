class APIError(Exception):
    def __init__(self, message="API error"):
        super().__init__(message)


class APIRateLimit(APIError):
    def __init__(self, message="API rate limit"):
        super().__init__(message)


class NotDownloadedError(Exception):
    def __init__(self, message="Not downloaded"):
        super().__init__(message)
