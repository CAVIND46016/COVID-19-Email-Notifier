import logging as log
from datetime import datetime
from os.path import join, basename, splitext
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from settings import LOGS_DIR, PATH_TO_CHROME_DRIVER


def get_browser(extensions=False, notifications=False, incognito=False):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    if not extensions:
        chrome_options.add_argument("--disable-extensions")

    if not notifications:
        chrome_options.add_argument("--disable-notifications")

    if incognito:
        chrome_options.add_argument("--incognito")

    driver = webdriver.Chrome(executable_path=PATH_TO_CHROME_DRIVER, options=chrome_options)
    return driver


def logger(log_file_name, suffix=None):
    """
    Args:
    log_file_name<str>: Basename of the log file
    suffix <str>: The suffix that is appended to the name of the log_file
    """

    suffix_dir = {'date': '%Y-%m-%d',
                  'timestamp': '%Y-%m-%d_%H%M%S',
                  'week_of_year': '%W',
                  'day_of_year': "%j",
                  'week_num': '%w'
                  }
    try:
        append_str = f"_{datetime.now().strftime(suffix_dir[suffix])}"
    except KeyError:
        append_str = ""

    log_file = join(LOGS_DIR, splitext(basename(log_file_name))[0] + append_str + '.log')
    log.basicConfig(filename=log_file,
                    filemode='a',
                    level=log.INFO,
                    format='%(asctime)s %(levelname)s : %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p')
    return log
