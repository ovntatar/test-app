from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipient, template, **kwargs):
    """
    Send email (only in production mode)
    
    Args:
        subject: Email subject
        recipient: Recipient email address
        template: Template name (without extension)
        **kwargs: Variables to pass to template
    """
    app = current_app._get_current_object()
    
    # In development, just print and return
    if app.config.get('MAIL_SUPPRESS_SEND', True):
        print(f"\n{'='*60}")
        print(f"📧 EMAIL (DEV MODE - NOT SENT)")
        print(f"{'='*60}")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Template: {template}")
        print(f"Variables: {kwargs}")
        print(f"{'='*60}\n")
        return
    
    # In production, send real email
    msg = Message(
        subject=f"[{app.config['APP_NAME']}] {subject}",
        recipients=[recipient],
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Render HTML and text versions
    msg.html = render_template(f'emails/{template}.html', **kwargs)
    try:
        msg.body = render_template(f'emails/{template}.txt', **kwargs)
    except:
        # If text version doesn't exist, use a simple fallback
        msg.body = f"Please view this email in an HTML-compatible email client."
    
    # Send asynchronously
    Thread(target=send_async_email, args=(app, msg)).start()

def send_confirmation_email(user, token, confirmation_url):
    """Send email confirmation"""
    send_email(
        subject="Confirm Your Email Address",
        recipient=user.email,
        template="confirm_email",
        user=user,
        confirmation_url=confirmation_url
    )

def send_password_reset_email(user, token, reset_url):
    """Send password reset email"""
    send_email(
        subject="Password Reset Request",
        recipient=user.email,
        template="reset_password",
        user=user,
        reset_url=reset_url
    )

def send_welcome_email(user):
    """Send welcome email after confirmation"""
    send_email(
        subject="Welcome to " + current_app.config['APP_NAME'],
        recipient=user.email,
        template="welcome",
        user=user
    )

def send_plan_change_email(user, old_plan, new_plan):
    """Send email when user changes plan"""
    send_email(
        subject="Plan Changed",
        recipient=user.email,
        template="plan_change",
        user=user,
        old_plan=old_plan,
        new_plan=new_plan
    )

def send_subscription_cancelled_email(user, plan):
    """Send email when subscription is cancelled"""
    send_email(
        subject="Subscription Cancelled",
        recipient=user.email,
        template="subscription_cancelled",
        user=user,
        plan=plan
    )

def send_payment_success_email(user, plan, amount):
    """Send email after successful payment"""
    send_email(
        subject="Payment Successful",
        recipient=user.email,
        template="payment_success",
        user=user,
        plan=plan,
        amount=amount
    )
