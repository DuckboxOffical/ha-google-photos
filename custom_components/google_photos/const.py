"""Constants for the Google Photos integration."""

DOMAIN = "google_photos"
INTEGRATION_NAME = "Google Photos"

# OAuth 2.0 scopes
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
]

# Google Photos API endpoints
PICKER_API_BASE = "https://photoslibrary.googleapis.com/v1"
PICKER_SESSION_ENDPOINT = f"{PICKER_API_BASE}/picker:createSession"
PICKER_POLL_ENDPOINT = f"{PICKER_API_BASE}/picker:poll"
OAUTH_TOKEN_URI = "https://oauth2.googleapis.com/token"
OAUTH_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"

# Configuration
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_ALBUM_ID = "album_id"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_SLIDESHOW_INTERVAL = "slideshow_interval"

# Defaults
DEFAULT_UPDATE_INTERVAL = 3600  # 1 hour
DEFAULT_SLIDESHOW_INTERVAL = 10  # 10 seconds

# Attributes
ATTR_ALBUM_NAME = "album_name"
ATTR_PHOTO_COUNT = "photo_count"
ATTR_CURRENT_PHOTO = "current_photo"
ATTR_PHOTO_URL = "photo_url"

