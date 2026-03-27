'''
Copyright (c) 2022 University of Memphis, mDOT Center. All rights reserved. 

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer. 

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution. 

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from importlib import import_module

from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from decouple import config as env_config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home', 'api'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    app.jinja_env.policies["json.dumps_kwargs"] = {"sort_keys": False}
    mail.init_app(app)
    
    # @app.context_processor
    # def inject_clarity_user():
    #     clarity_user_id = None

    #     if getattr(current_user, "is_authenticated", False):
    #         clarity_user_id = str(current_user.get_id())

    #     return {
    #         "CLARITY_USER_ID": clarity_user_id,
    #         "CLARITY_PROJECT_ID": env_config("CLARITY_PROJECT_ID")
    #     }
    
    @app.context_processor
    def inject_posthog_user():
        posthog_user_id = None
        posthog_email = None
        posthog_displayname = None

        if getattr(current_user, "is_authenticated", False):
            posthog_user_id = str(current_user.get_id())
            posthog_email = str(current_user.email)
            posthog_displayname = str(current_user.displayname)

        return {
            "POSTHOG_USER_ID": posthog_user_id,
            "POSTHOG_EMAIL": posthog_email,
            "POSTHOG_DISPLAYNAME": posthog_displayname
        }
    return app
