from flask import Blueprint
bp = Blueprint("account", __name__, template_folder='../../templates')
from . import routes  # noqa
