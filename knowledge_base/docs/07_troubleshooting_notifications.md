# Troubleshooting: Notifications

## Not Receiving Email Notifications

1. **Check spam/junk folder**: Email providers sometimes filter TaskFlow emails. Look for emails from noreply@taskflow.io.
2. **Add TaskFlow to your contacts**: Add noreply@taskflow.io to your email contacts or safe senders list to prevent filtering.
3. **Verify notification settings**: Go to Account Settings → Notifications → Email. Ensure the notification types you want are enabled.
4. **Check project-level settings**: You can mute notifications per project. Go to the project → Settings → Notifications to check if you've accidentally muted it.
5. **Verify your email address**: Go to Account Settings → Profile. Ensure your email is correct and verified (a green checkmark should appear next to it).

Email notifications are sent in real-time for direct @mentions and task assignments. For other events (comments, status changes), TaskFlow batches notifications and sends a digest every 15 minutes to avoid flooding your inbox. You can switch to real-time delivery in notification settings.

## Not Receiving Push Notifications (Mobile)

1. **Check device notification settings**: On iOS, go to Settings → Notifications → TaskFlow → ensure "Allow Notifications" is on. On Android, go to Settings → Apps → TaskFlow → Notifications → ensure notifications are enabled.
2. **Check in-app settings**: Open the TaskFlow mobile app → Settings → Notifications. Ensure the types you want are enabled.
3. **Check Do Not Disturb**: If you've set DND hours in TaskFlow's notification settings, notifications are silenced during those times. They'll be delivered silently and visible when you open the app.
4. **Reinstall the app**: If push notifications stop working after an OS update, uninstall and reinstall TaskFlow. This refreshes the push notification token.

## Too Many Notifications

If you're overwhelmed by notifications:

- **Mute specific projects**: Go to the project → click the bell icon → select "Mute." You'll stop receiving notifications for that project but can still access it.
- **Watch only specific tasks**: Instead of watching entire projects, click "Watch" only on tasks you care about.
- **Switch to digest mode**: In notification settings, switch from real-time to digest delivery. You'll receive a summary every 15 minutes instead of individual notifications.
- **Set DND hours**: Under notification settings, set Do Not Disturb hours (e.g., 8 PM to 8 AM) during which no notifications are sent.

## Notification Preferences by Role

- **Admins** receive notifications for all workspace-level events (new members, billing alerts, plan changes) in addition to task-level notifications.
- **Members** receive task-level notifications only (assignments, comments, mentions, due dates).
- **Viewers** receive notifications only when they are @mentioned in a comment.
