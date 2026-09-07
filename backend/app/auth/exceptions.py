"""Authentication exceptions."""

class AuthError(Exception):
    """Base class for all authentication errors."""
    pass

class MissingTokenError(AuthError):
    """Raised when the authorization token is completely missing."""
    pass

class MalformedTokenError(AuthError):
    """Raised when the authorization header is present but malformed (e.g. not Bearer)."""
    pass

class InvalidTokenError(AuthError):
    """Raised when the token is invalid or cannot be verified."""
    pass

class ExpiredTokenError(AuthError):
    """Raised when the verified token has expired."""
    pass
