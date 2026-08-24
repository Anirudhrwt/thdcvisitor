"""
app.py
-------
The entry point that ties everything together. It:
  1. Creates the Flask app
  2. Makes sure the database + head admin account exist
  3. Registers each feature's routes (Blueprints) from their
     own files:
       - visitor_routes.py    -> visitor form + OTP verification
       - auth_routes.py       -> login / logout
       - dashboard_routes.py  -> unified admin dashboard

This file itself defines no routes - it only wires the pieces
together, so each feature's logic lives in exactly one place.
"""

from flask import Flask

import config
import database
from visitor_routes import visitor_bp
from auth_routes import auth_bp
from dashboard_routes import dashboard_bp

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Make sure database + head admin account exist before the app serves any page
database.init_db()

# Register each feature's routes
app.register_blueprint(visitor_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)


if __name__ == "__main__":
    app.run(debug=True)
