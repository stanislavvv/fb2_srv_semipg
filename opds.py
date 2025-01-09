#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""development/testing opds app start file"""

from app import create_app
if __name__ == "__main__":
    app = create_app()
    print(app.url_map)
    app.run(host='0.0.0.0', port=8000)
