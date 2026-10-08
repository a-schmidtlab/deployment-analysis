"""Allow ``python -m deployment_analyzer``."""

import sys

from .cli import main

sys.exit(main())
