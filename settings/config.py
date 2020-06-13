"""
General configuration settings
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

PATH_TO_CHROME_DRIVER = os.path.join(RESOURCES_DIR, "chromedriver.exe")
