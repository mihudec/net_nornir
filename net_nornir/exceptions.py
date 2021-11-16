import re

class NetNornirException(Exception):
    pass

class ErrorOutputException(NetNornirException):
    pass

class InvalidCommand(ErrorOutputException):
    pass

class AmbiguousCommand(ErrorOutputException):
    pass

class PolicyMapPresent(ErrorOutputException):
    

    def get_current_pm_name(self):
        match = re.search(pattern=r"PM: '(?P<pm_name>\S+)'", string=repr(self))
        if match:
            return match.group('pm_name')