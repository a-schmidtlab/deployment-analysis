"""Entry point of the frozen (PyInstaller) build."""

import sys

from deployment_analyzer.cli import main

sys.exit(main())
