from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from settings import PATH_TO_CHROME_DRIVER


def get_browser(
    executable_path=PATH_TO_CHROME_DRIVER,
    headless=False,
    incognito=False,
    sandbox=False,
    extensions=False,
    notifications=False,
    dev_shm_usage=False,
):
    """
    Creates and returns a Selenium WebDriver instance for Chrome.

    :param executable_path: Path to the Chrome driver executable.
    :param headless: Whether to run Chrome in headless mode (without GUI).
    :param incognito: Whether to launch Chrome in incognito mode.
    :param sandbox: Whether to disable the sandbox for Chrome.
    :param extensions: Whether to disable Chrome extensions.
    :param notifications: Whether to disable Chrome notifications.
    :param dev_shm_usage: Whether to disable the use of /dev/shm for shared memory in Chrome.
    :return: Selenium WebDriver instance for Chrome.
    """

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

    if incognito:
        chrome_options.add_argument("--incognito")

    if not sandbox:
        chrome_options.add_argument("--no-sandbox")

    if not extensions:
        chrome_options.add_argument("--disable-extensions")

    if not notifications:
        chrome_options.add_argument("--disable-notifications")

    if not dev_shm_usage:
        chrome_options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(
        executable_path=executable_path,
        options=chrome_options
    )
