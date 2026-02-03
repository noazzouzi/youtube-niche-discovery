# Deprecated Files Cleanup Notes

**Date:** 2025-02-03  
**Task:** Technical debt cleanup

## Files Moved to deprecated/

### Backup Files (safe to delete)
- `enhanced_ui_server_invidious_backup.py` - Old backup before yt-dlp migration
- `enhanced_ui_server_original_backup.py` - Original version backup
- `enhanced_ui_server_refactored.py` - Intermediate refactoring version

### Obsolete Server Files (superseded by enhanced_ui_server.py)
- `demo-api.py` - FastAPI demo version
- `simple_server.py` - Early simple version
- `production_server.py` - Earlier production version
- `live_api_server.py` - Used YouTube API directly (has hardcoded key!)
- `secure_live_server.py` - Secure version of live_api_server
- `enhanced_server.py` - Earlier enhanced version
- `deploy_niche_engine.py` - Old deployment script

### Obsolete Test/Demo Files
- `test_invidious.py` - Tests for deprecated Invidious API
- `test_channels.py` - Broken (wrong get_shared_components signature)
- `test_channels_mock.py` - Mock tests for old API
- `demo_example.py` - Outdated demo (wrong API signature)

## Dead Code in enhanced_ui_server.py (NOT removed to avoid breaking server)

The following dead code exists but was left in place:

1. **`InvidiousAPI` class (lines ~320-537)** - Never instantiated, completely dead
2. **`YtDlpClient` class (lines ~109-319)** - Never used, `_ytdlp_client` always None
3. **DEPRECATED methods (lines ~731-739)** - `_search_channels()` and `_get_channel_statistics()`
4. **Confusing variable naming** - `invidious_api` variable actually holds `YtDlpDataSource`

## Current Architecture

**Main server:** `enhanced_ui_server.py`  
**Data source:** `ytdlp_data_source.py` (YtDlpDataSource class)  
**No API keys needed** - uses yt-dlp for YouTube data extraction

## Future Cleanup (optional)

To fully clean enhanced_ui_server.py:
1. Remove `InvidiousAPI` class entirely
2. Remove `YtDlpClient` class  
3. Remove `_ytdlp_client` global variable
4. Rename `invidious_api` variable to `ytdlp_source` everywhere
5. Remove DEPRECATED methods

This would reduce the file from ~2400 lines to ~1900 lines.
