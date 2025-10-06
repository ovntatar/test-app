import click
from flask import current_app
from werkzeug.security import generate_password_hash
from . import db
from .models import User

@click.group()
def cli():
    pass

@cli.command("create-admin")
@click.argument("email")
@click.argument("password")
def create_admin(email, password):
    """Create an admin user."""
    u = User.query.filter_by(email=email).first()
    if u:
        click.echo("User exists; updating role to admin and password...")
        u.role = "admin"
        u.password_hash = generate_password_hash(password)
    else:
        u = User(email=email, role="admin", password_hash=generate_password_hash(password))
        db.session.add(u)
    db.session.commit()
    click.echo("Admin ready: %s" % email)
