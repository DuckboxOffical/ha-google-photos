# Google Photos Integration for Home Assistant

A custom Home Assistant integration that uses the new Google Photos Picker API to display a slideshow of your Google Photos on your wall panel.

## Features

- ✅ Uses the new Google Photos Picker API (replaces deprecated Library API)
- ✅ OAuth 2.0 authentication with Google
- ✅ Camera entity for slideshow display
- ✅ Configurable slideshow intervals
- ✅ Support for specific albums or all photos
- ✅ Custom Lovelace card for wall panel display
- ✅ Automatic token refresh

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add this repository URL: `https://github.com/DuckboxOffical/ha-google-photos`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Google Photos" and install it

### Method 2: Manual Installation

1. Copy the `custom_components/google_photos` folder to your Home Assistant `custom_components` directory
2. Copy the `www/community/google-photos-slideshow-card.js` to your `www/community` directory
3. Restart Home Assistant

## Setup

### 1. Create Google OAuth 2.0 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Photos Library API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Photos Library API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `https://your-home-assistant-url/auth/external/callback`
     - Replace `your-home-assistant-url` with your Home Assistant URL
   - Click "Create"
   - Copy the **Client ID** and **Client Secret**

### 2. Configure the Integration

1. In Home Assistant, go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **Google Photos**
4. Enter your **Client ID** and **Client Secret**
5. Complete the OAuth flow by authorizing access to your Google Photos
6. Configure options (optional):
   - **Album ID**: Leave empty for all photos, or enter a specific album ID
   - **Update Interval**: How often to refresh the photo list (default: 3600 seconds)
   - **Slideshow Interval**: How long each photo displays (default: 10 seconds)

### 3. Find Album ID (Optional)

If you want to display photos from a specific album:

1. Go to [Google Photos](https://photos.google.com/)
2. Open the album you want to use
3. Look at the URL - it will contain something like `albumid=ABC123...`
4. Copy the album ID and paste it into the integration options

## Usage

### Basic Camera Entity

The integration creates a `camera.google_photos` entity that you can use in any camera card:

```yaml
type: camera
entity: camera.google_photos
```

### Wall Panel Slideshow Card

For a better wall panel experience, use the custom Lovelace card:

1. Add the card resource in your Lovelace configuration:
   ```yaml
   resources:
     - url: /local/community/google-photos-slideshow-card.js
       type: module
   ```

2. Add the card to your dashboard:
   ```yaml
   type: custom:google-photos-slideshow-card
   entity: camera.google_photos
   interval: 10
   transition: fade
   transition_duration: 1000
   show_info: true
   fullscreen: true
   ```

### Card Configuration Options

- `entity` (required): The camera entity ID (e.g., `camera.google_photos`)
- `interval`: Slideshow interval in seconds (default: 10)
- `transition`: Transition effect - `fade` or `none` (default: `fade`)
- `transition_duration`: Transition duration in milliseconds (default: 1000)
- `show_info`: Show album name and photo count overlay (default: `true`)
- `fullscreen`: Enable fullscreen mode (default: `true`)

## Troubleshooting

### Integration won't authenticate

- Make sure you've enabled the Google Photos Library API in Google Cloud Console
- Verify your redirect URI matches exactly: `https://your-home-assistant-url/auth/external/callback`
- Check that your Client ID and Client Secret are correct

### No photos showing

- Verify you have photos in your Google Photos account
- If using an album ID, make sure it's correct
- Check the Home Assistant logs for errors
- Try increasing the update interval

### Photos not updating

- The integration updates photos based on the "Update Interval" setting
- Check that your token hasn't expired (it should auto-refresh)
- Restart Home Assistant if issues persist

## API Notes

This integration uses the new Google Photos Picker API, which was introduced in March 2025. The old Library API no longer provides access to photos not uploaded by your application, so this integration uses the Picker API flow to allow users to select photos and albums.

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/lincolnduck/ha-google-photos/issues)

## License

This project is licensed under the MIT License.

