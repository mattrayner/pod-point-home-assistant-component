"""Custom errors for integration"""


class PodPointAPIError(Exception):
    pass


class PodPointSessionError(PodPointAPIError):
    pass


class PodPointAuthError(PodPointAPIError):
    pass