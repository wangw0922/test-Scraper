from flask import Blueprint
from ..TunnelAgent import TunnelAgent



TA = TunnelAgent()
agent_blu = Blueprint("AgentControl", __name__)

from . import views
