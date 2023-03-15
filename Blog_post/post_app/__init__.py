from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'AbCdEfGhIjKl'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from post_app import models, application