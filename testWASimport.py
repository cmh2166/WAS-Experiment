import os
import re
import json
import time
import logging
import pytest
try:
    from unittest.mock import patch, call, MagicMock  # Python 3
except ImportError:
    from mock import patch, call, MagicMock  # Python 2

import WASimport

logging.basicConfig(filename="test.log", level=logging.INFO)

# Authenticate to WASAPI endpoint

# Get Variables from CLI

# Get JSON for Collection ID

# Get JSON for Date Before

# Get JSON for Date After

# Get JSON for Crawl / Job ID

# Get JSON for Type WARC or Other

# Get JSON with no Arguments
