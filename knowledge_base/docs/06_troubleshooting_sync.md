# Troubleshooting: Sync and Performance

## Tasks Not Syncing Across Devices

If changes made on one device aren't showing on another:

1. **Check internet connection** on both devices.
2. **Force a manual sync**: On web, press `Ctrl+Shift+R` to hard refresh. On mobile, pull down on any screen.
3. **Verify you're in the same workspace**: If you belong to multiple workspaces, ensure both devices are viewing the same one.
4. **Check TaskFlow status**: Visit status.taskflow.io for any ongoing service incidents. Sync delays occasionally occur during scheduled maintenance (announced 48 hours in advance via email).
5. **Log out and back in**: This forces a full resync with the server.

Sync between web and mobile typically happens within 10 seconds. Google Calendar sync runs every 5 minutes. Slack notifications are near-instant.

## Slow Loading or Performance Issues

**On Web:**
- Clear browser cache and cookies for taskflow.io.
- Disable browser extensions temporarily — ad blockers and privacy extensions sometimes interfere with TaskFlow's real-time sync.
- Try a different browser to rule out browser-specific issues.
- If a specific board is slow, it may have too many cards. Boards with over 500 active cards can experience rendering delays. Archive completed tasks regularly to keep boards fast.
- Check your internet speed. TaskFlow requires a minimum of 2 Mbps for smooth operation.

**On Mobile:**
- Ensure you're running the latest app version.
- Restart the app (close completely and reopen).
- On Android, clear the app cache: Settings → Apps → TaskFlow → Clear Cache.
- Boards with many cards load slower on mobile. Use filters to reduce the visible card count.

## Real-Time Collaboration Lag

When multiple people edit the same board simultaneously:

- Changes should appear within 1-2 seconds for all users.
- If you notice lag beyond 5 seconds, one or more users may have a slow internet connection.
- TaskFlow uses conflict resolution for simultaneous edits to the same task. The last saved change wins, but the activity log preserves both edits.

## Data Not Updating After Bulk Import

If you've imported tasks via CSV and they're not appearing:

- CSV import processes in the background. Large imports (500+ tasks) can take up to 10 minutes.
- Check the import status in Project Settings → Import/Export → Import History.
- If the import shows errors, download the error log. Common issues include: missing required columns (Title is mandatory), dates in wrong format (use YYYY-MM-DD), and assignee emails not matching existing workspace members.
