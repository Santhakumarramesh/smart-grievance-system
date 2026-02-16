from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import Config

class EmailService:
    @staticmethod
    def send_email(to_email, subject, body):
        """
        Send email via Gmail SMTP or print to console
        """
        if Config.DEMO_EMAIL_MODE:
            print(f"\n{'='*60}")
            print(f"[DEMO EMAIL MODE]")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            return True
        
        # Real email sending via Gmail SMTP
        try:
            if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
                print("⚠ Email credentials not configured. Set MAIL_USERNAME and MAIL_PASSWORD")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = Config.MAIL_DEFAULT_SENDER
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create HTML version
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <div style="background: linear-gradient(135deg, #2563eb, #1e40af); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                            <h2 style="margin: 0;">Smart Grievance System</h2>
                        </div>
                        <div style="padding: 20px; background: #f9fafb;">
                            <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{body}</pre>
                        </div>
                        <div style="padding: 15px; background: #e5e7eb; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px;">
                            <p style="margin: 0;">This is an automated message from Smart Grievance System</p>
                            <p style="margin: 5px 0 0 0;">Please do not reply to this email</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Attach both plain text and HTML
            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                server.starttls()
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"✓ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            # Fallback to console
            print(f"\n{'='*60}")
            print(f"[EMAIL FALLBACK - Console Output]")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            return False
    
    @staticmethod
    def send_grievance_notification(user_email, grievance_id, department, status, message):
        """
        Send notification about grievance update
        """
        subject = f"Grievance #{grievance_id} - Status Update: {status}"
        
        # Create tracking URL (in production, use actual domain)
        tracking_url = f"http://localhost:5000/track.html?id={grievance_id}"
        
        body = f"""
Dear Citizen,

Your grievance has been updated:

Complaint ID: #{grievance_id}
Department: {department}
Current Status: {status}

Update Details:
{message}

You can track your complaint at:
{tracking_url}

Thank you for using the Smart Grievance System.

---
This is an automated message. Please do not reply.
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_welcome_email(user_email, user_name):
        """
        Send welcome email after registration
        """
        subject = "Welcome to Smart Grievance System"
        
        body = f"""
Dear {user_name},

Welcome to the Smart Grievance Classification and Resolution Tracking System!

Your account has been successfully created and verified.

You can now:
- Submit grievances
- Track complaint status in real-time
- Receive updates via email

Login at: http://localhost:5000/login.html

Thank you for trusting us with your concerns.

Best regards,
Smart Grievance System Team
        """
        
        return EmailService.send_email(user_email, subject, body)
