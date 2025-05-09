import sys
sys.path.append('../')
from xinwei.project.Control.app.api import *
from flask import Flask
from gevent import pywsgi, monkey
import logging
import coloredlogs
import threading
from xinwei.project.Control.app.setting import HOST, PORT


logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s:%(message)s')
coloredlogs.install(level='INFO')
monkey.patch_all(thread=False)
app = Flask(__name__)

app.register_blueprint(edition_blu)
app.register_blueprint(agent_blu)
app.register_blueprint(token_blu)
app.register_blueprint(QUIT_BLU)


@app.route('/', methods=['get'])
def hello():
    return 'Xinwei  central control system'


def main():
    words = f'Running on http://{HOST}:{PORT}'
    logging.info(words)
    server = pywsgi.WSGIServer((HOST, PORT), app)
    server.serve_forever()


if __name__ == '__main__':
    thread1 = threading.Thread(target=main)
    thread2 = threading.Thread(target=TunnelAgent().updateRegular)
    thread1.start()
    thread2.start()
