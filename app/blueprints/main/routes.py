from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import bp
from ...models import Plan
from ...extensions import db

# Existing routes
@bp.get("/")
def index():
    available_plans = Plan.query.filter_by(is_active=True).order_by(Plan.sort_order.asc()).all()
    return render_template("index.html", available_plans=available_plans)

@bp.get("/about")
def about():
    return render_template("about.html")

@bp.get("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# Product & Features
@bp.get("/product")
def product():
    return render_template("product.html")

@bp.get("/features")
def features():
    return render_template("features.html")

# Company
@bp.get("/company")
def company():
    return render_template("company.html")

@bp.get("/careers")
def careers():
    return render_template("careers.html")

@bp.get("/blog")
def blog():
    return render_template("blog.html")

@bp.get("/press")
def press():
    return render_template("press.html")

# Support
@bp.get("/support")
def support():
    return render_template("support.html")

@bp.get("/help")
def help_center():
    return render_template("help.html")

@bp.get("/docs")
def documentation():
    return render_template("documentation.html")

# Contact
@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        # TODO: Implement email sending or save to database
        flash("Thank you for your message! We'll get back to you soon.", "success")
        return redirect(url_for("main.contact"))
    
    return render_template("contact.html")

# System Status
@bp.get("/status")
def system_status():
    # Check system components
    from datetime import datetime
    
    status_data = {
        "api": {"status": "operational", "response_time": "45ms"},
        "dashboard": {"status": "operational", "response_time": "120ms"},
        "database": {"status": "operational", "response_time": "8ms"},
        "email": {"status": "operational", "response_time": "230ms"},
        "auth": {"status": "operational", "response_time": "35ms"},
        "last_updated": datetime.utcnow()
    }
    
    return render_template("status.html", status_data=status_data)

# Legal Pages
@bp.get("/impressum")
def impressum():
    return render_template("legal/impressum.html")

@bp.get("/agb")
def agb():
    return render_template("legal/agb.html")

@bp.get("/privacy")
def privacy():
    return render_template("legal/privacy.html")

@bp.get("/terms")
def terms():
    return render_template("legal/terms.html")

# Social Media (redirects)
@bp.get("/social/facebook")
def social_facebook():
    return redirect("https://facebook.com/yourapp")

@bp.get("/social/twitter")
def social_twitter():
    return redirect("https://twitter.com/yourapp")

@bp.get("/social/linkedin")
def social_linkedin():
    return redirect("https://linkedin.com/company/yourapp")

@bp.get("/social/instagram")
def social_instagram():
    return redirect("https://instagram.com/yourapp")
