"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging,
security headers, and SQL database
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from service import config
from service.common import log_handlers

# Debug: print the database URL
print("DATABASE_URL =", os.getenv("DATABASE_URL"))

# Create Flask application
app = Flask(__name__)
# Override default config and apply environment-based settings
app.config.from_object(config)
# Use environment variable for the database URI if provided
if os.getenv("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Suppress track modifications warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Enable security headers
Talisman(app)

# Initialize logging
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

# Initialize database ORM
db = SQLAlchemy(app)

# Import routes and models after app and db are set up
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routes, models  # noqa: F401 E402
# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Create or migrate tables
try:
    models.init_db(app)  # make sure our database tables exist
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # Gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
