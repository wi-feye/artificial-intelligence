from flask import Flask
from config import Config

app = None


def create_app():
    global app

    app = Flask(__name__)
    app.config.from_object(Config)

    # env = Environments(app)
    # env.from_object(Config)



#    from src import routes

    app.app_context().push()

    return app
    