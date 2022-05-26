class AppException(Exception):
    ...


class LoadConfigError(AppException):
    ...


class ConfigKeyError(AppException):
    ...


class InvalidConfigError(AppException):
    ...
