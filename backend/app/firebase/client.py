"""Firebase Admin SDK initialization and client providers."""

import logging
from typing import Any
import firebase_admin
from firebase_admin import credentials, firestore, auth

from .config import get_firebase_settings
from .exceptions import FirebaseConfigError

logger = logging.getLogger(__name__)

def initialize_firebase() -> None:
    """Initialize the Firebase Admin SDK exactly once."""
    settings = get_firebase_settings()
    
    if settings.FIREBASE_TESTING:
        logger.info("FIREBASE_TESTING is True. Bypassing real Firebase initialization.")
        return

    # If already initialized, avoid double-initialization
    if firebase_admin._apps:
        return

    # Check for ADC credentials via envvar
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        logger.warning(
            "GOOGLE_APPLICATION_CREDENTIALS is not set. Assuming default ADC "
            "or running in GCP environment."
        )

    try:
        if settings.FIREBASE_PROJECT_ID:
            firebase_admin.initialize_app(options={"projectId": settings.FIREBASE_PROJECT_ID})
        else:
            # We initialize without explicit credentials parameter, which uses ADC 
            # (GOOGLE_APPLICATION_CREDENTIALS) implicitly.
            firebase_admin.initialize_app()
    except Exception as e:
        raise FirebaseConfigError(f"Failed to initialize Firebase Admin SDK: {e}")


def get_firestore_client() -> Any:
    """Return an active Cloud Firestore client."""
    settings = get_firebase_settings()
    if settings.FIREBASE_TESTING:
        raise FirebaseConfigError("Cannot get Firestore client while FIREBASE_TESTING is True")
        
    if not firebase_admin._apps:
        initialize_firebase()
    
    try:
        return firestore.client()
    except Exception as e:
        raise FirebaseConfigError(f"Failed to get Firestore client: {e}")


def get_auth_client() -> Any:
    """Return the Firebase Auth service."""
    settings = get_firebase_settings()
    if settings.FIREBASE_TESTING:
        raise FirebaseConfigError("Cannot get Firebase Auth client while FIREBASE_TESTING is True")
        
    if not firebase_admin._apps:
        initialize_firebase()
    
    return auth
