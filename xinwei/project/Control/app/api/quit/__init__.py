# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 10:15
# @Author  : 李文霖
from flask import Blueprint
from ..whether_quit import Quit

QUIT_BLU = Blueprint("quit", __name__)
Q = Quit()

from . import views
