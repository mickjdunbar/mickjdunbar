from definitions import PROPERTIES
import configparser
import logging
import json
import sys
from flask.wrappers import Response
import os
import datetime
import sys
import time
import json
import requests
from flask import Flask, session, jsonify, abort, make_response, redirect, request, url_for, copy_current_request_context
from flask_restful import Api, Resource, reqparse, fields, marshal
from os.path import dirname, join
from flask_httpauth import HTTPBasicAuth
from healthcheck import HealthCheck, EnvironmentDump
import uuid
import datetime
import time
from flask_cors import CORS, cross_origin
from rich import print
from time import strftime
import traceback
from waitress import serve

import requests
import fitz
import io


#########################################################################
# logging
#########################################################################
import cplogger
_logger = cplogger.CPLogger(
    __name__, PROPERTIES, default_extra=None)

#########################################################################
# Init
#########################################################################

GUID = str(uuid.uuid4())
ts = time.time()

# Get environment variables
API_PORT = int(PROPERTIES['default']['port'])
os.environ['TZ'] = PROPERTIES['server']['tz']

app = Flask(__name__, static_url_path='', static_folder='web/static')
app.secret_key = GUID
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True
app.port = API_PORT
api = Api(app)
auth = HTTPBasicAuth()
app.logger = _logger
app.config['SECRET_KEY'] = PROPERTIES['server']['secret']

health = HealthCheck(app, "/healthcheck")

"""
envdump = EnvironmentDump(app, "/environment",
                          include_python=True, include_os=False,
                          include_process=False, include_config=True)

"""


##################################################################################################################
# main
##################################################################################################################

def cp_available():
    ui_init_action = {
        ts: ts
    }
    return True, str(ui_init_action)

health.add_check(cp_available)

def do_extract(docurl, options):
    finalRespDict = {}
    url =docurl
    request = requests.get(url)
    filestream = io.BytesIO(request.content)
    pdf = fitz.open(stream=filestream, filetype="pdf")
    text=""
    for page in pdf:
        text += page.get_text()
    print(text)
    finalRespDict['text'] = text
    finalRespDict['length']=len(text.split())
    return finalRespDict

@app.route('/api/extract_text_pdf', methods=['POST'])
def extract_pdf():
        reqbody = request.get_json()
        if 'options' in reqbody:
            options = reqbody['options']
        docurl = reqbody['url']

        #process
        resp = do_extract(docurl, options)

        return resp, 200



@app.before_request
def log_request_info():
    _logger.info('__Headers: {headers}'.format(headers=request.headers))
    _logger.info('__Body: {body}'.format(body=request.get_data()))


@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    _logger.info('{timestamp} {remote_addr} {method} {scheme} {status}'.format(timestamp=timestamp, remote_addr=request.remote_addr,
                     method=request.method, scheme=request.scheme, full_path=request.full_path, status=response.status))
    return response


@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    _logger.error('{timestamp} {remote_addr} {method} {scheme} {path} *** 500 INTERNAL SERVER ERROR *** {tb}'.format(
        timestamp=timestamp, remote_addr=request.remote_addr, method=request.method, scheme=request.scheme, path=request.full_path, tb=tb))
    time.sleep(2)
    return Response({"EXCEPTION": "Internal Server Error"}, 500)

def check_auth(request):
    secret = PROPERTIES['server']['secret']
    header_secret = request.headers.get('Secret')
    if header_secret is None or secret != header_secret:
        # invalid request
        responsDict = {
            'request_id': str(uuid.uuid4()),
            'valid_auth' : False,
            'request_status_verbose': 'Invalid secret'
        }
        _logger.error("POST [RESP] " + request.base_url, extra=responsDict)
        return responsDict, 403
    else:
        responsDict = {
            'request_id': str(uuid.uuid4()),
            'valid_auth' : True,
            'request_status_verbose': 'valid secret'
                }
        _logger.info("POST [RESP] " + request.base_url, extra=responsDict)
        return responsDict, 200
#########################################################################
# main
#########################################################################

if __name__ == '__main__':
    # Run Server
    _logger.info("#################################################")
    _logger.info("#################################################")
    _logger.info("#################################################")

    _logger.info("### Cognigy Server Orchestrator starting with config", extra={
        'api_port': str(API_PORT),
        'version': PROPERTIES['version']['version'],
        'cp_orchestrator_id': GUID,
        'server_properties': PROPERTIES

    })
    # Run from the same directory as this script
    this_files_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(this_files_dir)

    # `url_prefix` is optional, but useful if you are serving app on a sub-dir
    # behind a reverse-proxy.
    #serve(app, host='127.0.0.1', port=5555, url_prefix='/my-app')
    n=len(sys.argv)
    if n == 2:
        HTTP_PORT = int(sys.argv[1])
    else:
        HTTP_PORT = API_PORT
    _logger.info("######################### Server API Proxy started on Port {port} ########################".format(port=HTTP_PORT))
    serve(app, host='0.0.0.0', port=HTTP_PORT)
