"""Firebase custom application exceptions."""

class FirebaseError(Exception):
    """Base class for all Firebase-related errors."""
    pass

class FirebaseConfigError(FirebaseError):
    """Raised when Firebase configuration is missing or invalid."""
    pass

class FirebaseUnavailableError(FirebaseError):
    """Raised when the Firebase/Firestore service is unreachable or fails."""
    pass
