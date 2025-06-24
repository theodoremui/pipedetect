"""Custom exceptions for PipeDetect."""


class PipeDetectError(Exception):
    """Base exception for PipeDetect."""
    pass


class DetectionError(PipeDetectError):
    """Raised when pose detection fails."""
    pass


class ValidationError(PipeDetectError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(PipeDetectError):
    """Raised when configuration is invalid."""
    pass


class FileProcessingError(PipeDetectError):
    """Raised when file processing fails."""
    pass


class OutputError(PipeDetectError):
    """Raised when output generation fails."""
    pass 