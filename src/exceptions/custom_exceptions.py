"""
Custom exceptions for Guard AI Security System
"""


class GuardApiError(Exception):
    """Raised when API requests fail"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class LoggingError(Exception):
    """Raised when logging operations fail"""
    def __init__(self, message: str, log_path: str = None):
        super().__init__(message)
        self.log_path = log_path


class ServiceUnavailableError(Exception):
    """Raised when required services are unavailable"""
    def __init__(self, service_name: str, url: str = None):
        message = f"Service '{service_name}' is unavailable"
        if url:
            message += f" at {url}"
        super().__init__(message)
        self.service_name = service_name
        self.url = url