#!/usr/bin/env python3
"""
Machine Uptime Issues Management System (MUIMS)
Main application entry point
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
