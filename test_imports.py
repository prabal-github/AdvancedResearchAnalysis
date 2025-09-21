#!/usr/bin/env python3
# Test script to debug imports

print("Testing imports...")

try:
    from flask import Flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print(f"✗ Flask import failed: {e}")

try:
    from flask_sqlalchemy import SQLAlchemy
    print("✓ Flask-SQLAlchemy imported successfully")
except ImportError as e:
    print(f"✗ Flask-SQLAlchemy import failed: {e}")

try:
    from flask_socketio import SocketIO
    print("✓ Flask-SocketIO imported successfully")
except ImportError as e:
    print(f"✗ Flask-SocketIO import failed: {e}")

try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
except ImportError as e:
    print(f"✗ yfinance import failed: {e}")

try:
    import pandas as pd
    print("✓ pandas imported successfully")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

print("Import testing complete!")
