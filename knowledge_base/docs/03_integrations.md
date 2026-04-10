# TaskFlow Integrations

TaskFlow connects with popular tools your team already uses. Integrations are available on Pro and Business plans only. Free plan users can connect one integration as a trial.

## Slack Integration

Connect TaskFlow to Slack to receive task notifications in your Slack channels.

**Setup:**
1. Go to Workspace Settings → Integrations → Slack.
2. Click "Connect to Slack" and authorize access.
3. Choose which Slack channel receives TaskFlow notifications.
4. Customize which events trigger notifications (task created, assigned, completed, commented, overdue).

**Features:**
- Receive real-time task updates in Slack.
- Create new TaskFlow tasks directly from Slack using `/taskflow create [task name]`.
- Mark tasks as complete from Slack using `/taskflow done [task ID]`.

## Google Calendar Integration

Sync TaskFlow due dates with Google Calendar.

**Setup:**
1. Go to Workspace Settings → Integrations → Google Calendar.
2. Sign in with your Google account and grant calendar permissions.
3. Choose whether to sync all projects or only selected ones.

**Features:**
- Task due dates appear as calendar events.
- Moving a calendar event automatically updates the task's due date in TaskFlow.
- Two-way sync runs every 5 minutes. Manual sync available via the "Sync Now" button.

## GitHub Integration

Link GitHub repositories to TaskFlow projects for development workflow tracking.

**Setup:**
1. Go to Workspace Settings → Integrations → GitHub.
2. Authenticate with GitHub and select repositories.
3. Link a repository to a specific TaskFlow project.

**Features:**
- Automatically create TaskFlow tasks from GitHub issues.
- Task cards show linked pull request status (open, merged, closed).
- Commit messages referencing a TaskFlow task ID (e.g., `TF-123`) auto-link to that task.
- PR merges can automatically move linked tasks to a specified list (e.g., "Done").

## Webhook API

For custom integrations, TaskFlow offers a webhook API. Configure outgoing webhooks for any task event. Webhooks send JSON payloads to your specified URL. Documentation available at docs.taskflow.io/api/webhooks. Webhook support is available on Business plan only.
