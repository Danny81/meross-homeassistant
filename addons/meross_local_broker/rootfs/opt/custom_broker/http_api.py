import logging

from flask import Flask
from flask.logging import default_handler

from blueprints.auth import auth_blueprint
from blueprints.devs import devs_blueprint
from blueprints.profile import profile_blueprint
from codes import ErrorCodes
from database import db_session, init_db
from messaging import make_api_response
from model.exception import HttpApiError, BadRequestError

_LOG_URL = "/v1/log/user"
_DEV_LIST = "/v1/Device/devList"
_HUB_DUBDEV_LIST = "/v1/Hub/getSubDevices"
_LOGOUT_URL = "/v1/Profile/logout"


_LOGGER = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(auth_blueprint, url_prefix="/v1/Auth")
app.register_blueprint(profile_blueprint, url_prefix="/v1/Profile")
app.register_blueprint(devs_blueprint, url_prefix="/_devs_")
#app.register_blueprint(device_bludprint)
#app.register_blueprint(hub_blueprint)


root = logging.getLogger()
root.addHandler(default_handler)

# TODO: make this configurable
root.setLevel(logging.DEBUG)

init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.errorhandler(Exception)
def handle_exception(e):
    _LOGGER.exception("Uncaught exception: %s", str(e))
    return make_api_response(data=None, info=str(e), api_status=ErrorCodes.CODE_GENERIC_ERROR, status_code=500)


@app.errorhandler(BadRequestError)
def handle_bad_exception(e):
    _LOGGER.exception("BadRequest error: %s", e.msg)
    return make_api_response(data=None, info=e.msg, api_status=ErrorCodes.CODE_GENERIC_ERROR, status_code=400)


@app.errorhandler(HttpApiError)
def handle_http_exception(e):
    _LOGGER.error("HttpApiError: %s", e.error_code.name)
    return make_api_response(data=None, info=e.error_code.name, api_status=e.error_code)


