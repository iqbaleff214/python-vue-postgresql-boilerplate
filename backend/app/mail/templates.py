from app.core.config import settings


def reset_password_email(user_name: str, reset_link: str) -> tuple[str, str]:
    """Return (subject, html_body) for a password reset email."""
    subject = f"{settings.app_name} - Reset Your Password"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#f3f4f6; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6; padding:40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="background: linear-gradient(135deg, #1e1b4b, #312e81, #581c87); padding:32px 40px;">
                                <h1 style="margin:0; color:#ffffff; font-size:20px; font-weight:600;">{settings.app_name}</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:40px;">
                                <h2 style="margin:0 0 16px; color:#111827; font-size:22px; font-weight:700;">Reset Your Password</h2>
                                <p style="margin:0 0 24px; color:#6b7280; font-size:15px; line-height:1.6;">
                                    Hi {user_name},<br><br>
                                    We received a request to reset your password. Click the button below to choose a new password.
                                    This link will expire in {settings.reset_password_expire_minutes} minutes.
                                </p>
                                <table cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="border-radius:10px; background-color:#7c3aed;">
                                            <a href="{reset_link}" target="_blank"
                                               style="display:inline-block; padding:14px 32px; color:#ffffff; text-decoration:none; font-size:15px; font-weight:600;">
                                                Reset Password
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                <p style="margin:24px 0 0; color:#9ca3af; font-size:13px; line-height:1.6;">
                                    If you didn't request this, you can safely ignore this email. Your password will remain unchanged.
                                </p>
                                <hr style="margin:32px 0; border:none; border-top:1px solid #e5e7eb;">
                                <p style="margin:0; color:#9ca3af; font-size:12px;">
                                    If the button doesn't work, copy and paste this link into your browser:<br>
                                    <a href="{reset_link}" style="color:#7c3aed; word-break:break-all;">{reset_link}</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return subject, html_body
