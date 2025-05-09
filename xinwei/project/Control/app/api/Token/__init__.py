from flask import Blueprint
from ..TunnelAgent import TunnelAgent


TA = TunnelAgent()
token_blu = Blueprint("Token", __name__)

from . import views
