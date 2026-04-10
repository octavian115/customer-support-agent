# Troubleshooting: Login Issues

## Forgot Password

1. On the login page, click "Forgot password?"
2. Enter the email address associated with your TaskFlow account.
3. Check your inbox for a password reset email (arrives within 2 minutes).
4. Click the reset link — it expires after 1 hour.
5. Set a new password. Minimum 8 characters, must include at least one number and one special character.

If you don't receive the email, check your spam/junk folder. Add noreply@taskflow.io to your email contacts to prevent filtering.

## Two-Factor Authentication (2FA) Issues

TaskFlow supports 2FA via authenticator apps (Google Authenticator, Authy, etc.) and SMS.

**Lost access to your authenticator app:**
- Use one of the backup codes provided when you first set up 2FA. Each backup code can only be used once. Backup codes were shown during 2FA setup and also emailed to you.
- If you've lost your backup codes, contact support at support@taskflow.io with your account email and a photo of a government-issued ID. Account recovery takes 1-3 business days.

**Not receiving SMS codes:**
- Ensure your phone number is correct in Account Settings → Security → 2FA.
- Check that your phone has cellular service (SMS codes don't work over Wi-Fi).
- Some carriers delay SMS delivery. Wait up to 5 minutes before requesting a new code.
- You can request a maximum of 5 SMS codes per hour. After that, you'll be temporarily locked out for 30 minutes.

## Account Locked

Accounts are automatically locked after 5 consecutive failed login attempts. The lockout lasts 15 minutes, after which you can try again. If you suspect unauthorized access to your account, reset your password immediately and enable 2FA.

## SSO Login Issues

If your organization uses SSO (Single Sign-On) with TaskFlow:

- Ensure you're signing in with your organization email, not a personal email.
- SSO configuration is managed by your organization's IT admin. If SSO isn't working, contact your IT department first.
- If your organization recently changed SSO providers, your IT admin needs to update the SSO settings in TaskFlow's admin panel.
- SSO is available on Business plan only. Pro and Free users must log in with email/password or Google/GitHub SSO.

## Browser Compatibility

TaskFlow's web app works best on the latest versions of:

- Google Chrome (recommended)
- Mozilla Firefox
- Microsoft Edge
- Safari (macOS)

Internet Explorer is not supported. If you experience login issues on a supported browser, try clearing your browser cookies for taskflow.io and attempting to log in again.
