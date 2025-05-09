from flask import Blueprint
from ..TunnelAgent import TunnelAgent

TA = TunnelAgent()
edition_blu = Blueprint("Edition", __name__)
current_editions = '2.07'

from . import views
