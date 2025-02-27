#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Version information for DeploymentAnalyzer.
This file is used throughout the application to maintain consistent version information.
"""

# Follow Semantic Versioning (https://semver.org/)
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0

# Derived values
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
VERSION_FULL = f"DeploymentAnalyzer v{VERSION}"
VERSION_DATE = "2024-02-27"  # Update with each release

# For display in GUI and other locations
APP_NAME = "Deployment Analyzer"
APP_VERSION_DISPLAY = f"{APP_NAME} v{VERSION}"

# For file naming
DIST_NAME = f"DeploymentAnalyzer-{VERSION}" 