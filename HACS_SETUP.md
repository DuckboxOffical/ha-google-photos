# HACS Setup Instructions

If you're getting the error "The version 480474c for this integration can not be used with HACS", you need to create a GitHub release.

## Steps to Fix HACS Installation:

1. **Create a GitHub Release:**
   - Go to your repository: https://github.com/DuckboxOffical/ha-google-photos
   - Click on "Releases" (on the right side of the repository page)
   - Click "Create a new release" or "Draft a new release"
   - Tag version: `v1.0.0` (must start with 'v')
   - Release title: `v1.0.0` or `Initial Release`
   - Description: Add release notes (e.g., "Initial release of Google Photos integration")
   - Click "Publish release"

2. **After creating the release:**
   - Go back to HACS in Home Assistant
   - Try adding the repository again
   - HACS should now be able to install from the release tag

## Alternative: Use the main branch

If you prefer to use the main branch instead of releases:
- In HACS, when adding the repository, make sure to select "Integration" as the category
- The repository structure should be correct with `custom_components/google_photos/` containing all the integration files

## Verification Checklist:

- ✅ `hacs.json` file exists in root directory
- ✅ `hacs.json` file exists in `custom_components/google_photos/` directory
- ✅ `manifest.json` has a `version` field (currently "1.0.0")
- ✅ Repository structure is correct: `custom_components/google_photos/`
- ✅ All integration files are present

