from flask import Blueprint
admin_blueprint = Blueprint('administrator', __name__)

from . import view