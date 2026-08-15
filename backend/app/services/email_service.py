import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_smtp_email_sync(to_email: str, subject: str, html_content: str):
    """Synchronous SMTP helper executed in thread pool."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM or settings.SMTP_USER
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(msg["From"], [to_email], msg.as_string())


async def send_verification_otp_email(to_email: str, otp_code: str) -> bool:
    """Send a 6-digit verification OTP code to the target email address."""
    subject = f"{otp_code} is your Gravity Fund verification code"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; margin: 0; padding: 40px 20px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: #0f172a; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 32px; text-align: center; }}
            .badge {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
            .code-box {{ background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #3b82f6; padding: 20px; margin: 24px 0; }}
            .footer {{ font-size: 12px; color: #64748b; margin-top: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">Gravity Fund Verification</span>
            <h2 style="margin-top: 16px; color: #ffffff;">Verify Your Account</h2>
            <p style="color: #94a3b8; font-size: 14px;">Enter the following 6-digit verification code to complete your registration:</p>
            <div class="code-box">{otp_code}</div>
            <p style="color: #94a3b8; font-size: 13px;">This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
            <div class="footer">If you did not request this code, please ignore this email.</div>
        </div>
    </body>
    </html>
    """

    # 1. Option A: Resend API
    if settings.RESEND_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAILS_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                    },
                    timeout=10.0,
                )
                if res.status_code in (200, 201):
                    logger.info(f"Successfully sent OTP email via Resend API to {to_email}")
                    return True
                logger.error(f"Resend API error: {res.text}")
        except Exception as e:
            logger.error(f"Failed to send email via Resend API: {e}")

    # 2. Option B: SMTP Server (Gmail / SendGrid / Custom SMTP)
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            await asyncio.to_thread(_send_smtp_email_sync, to_email, subject, html_content)
            logger.info(f"Successfully sent OTP email via SMTP to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")

    # 3. Dev Fallback Mode: Prominent Console Log
    logger.warning("=" * 65)
    logger.warning(" [DEV OTP EMAIL VERIFICATION CODE]")
    logger.warning(f" Target Email : {to_email}")
    logger.warning(f" 6-Digit OTP  : {otp_code}")
    logger.warning(f" Valid For    : {settings.OTP_EXPIRE_MINUTES} Minutes")
    logger.warning(" (Fill SMTP_USER & SMTP_PASSWORD in backend/.env to send real emails)")
    logger.warning("=" * 65)
    
    return True
