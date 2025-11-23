# Troubleshooting the 500 Error

If you're getting a "500 Internal Server Error" when trying to configure the integration, please follow these steps:

## Step 1: Check Home Assistant Logs

1. Go to **Settings** > **System** > **Logs** in Home Assistant
2. Look for errors related to `google_photos` or `config_flow`
3. Copy the full error traceback (it will show the exact line causing the issue)

## Step 2: Common Issues

### Issue: Missing Dependencies
If you see import errors, make sure all dependencies are installed:
- `google-auth==2.23.4`
- `google-auth-oauthlib==1.1.0`
- `google-auth-httplib2==0.1.1`
- `aiohttp==3.9.1`

### Issue: OAuth2 Flow Error
If the error is related to OAuth2 flow:
- Make sure your Home Assistant has an external URL configured
- Check that the redirect URI in Google Cloud Console matches: `https://your-home-assistant-url/auth/external/callback`
- Verify your Client ID and Client Secret are correct

### Issue: Config Flow Loading Error
If the config flow itself won't load:
- Make sure all files are in the correct location: `custom_components/google_photos/`
- Check that `manifest.json` has the correct `version` field
- Restart Home Assistant after making changes

## Step 3: Enable Debug Logging

Add this to your `configuration.yaml` to get more detailed logs:

```yaml
logger:
  default: info
  logs:
    custom_components.google_photos: debug
```

Then restart Home Assistant and try again. The logs will show more details about what's happening.

## Step 4: Share the Error

If you're still having issues, please share:
1. The full error traceback from the logs
2. Your Home Assistant version
3. Whether you're using HACS or manual installation

