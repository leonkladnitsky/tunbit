from bestcaptchasolverapi3.bestcaptchasolverapi import BestCaptchaSolverAPI
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import json
from logging import getLogger
from datetime import datetime
from sys import platform, exc_info
from time import sleep, time

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, TimeoutException, \
    ElementClickInterceptedException
from selenium.webdriver import Remote, Chrome, ChromeOptions, DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_all_elements_located as all_visible, \
    element_to_be_clickable as clickable, presence_of_element_located as present, url_matches, url_to_be

logger = getLogger(__name__)

WAIT_001 = 0.01
WAIT_01 = 0.1
WAIT_05 = 0.5
WAIT_075 = 0.75
WAIT_SEC = 1

JS_SCROLL_DOWN = 'window.scrollTo(0, document.body.scrollHeight)'


def threaded(f, executor=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        return (executor or ThreadPoolExecutor()).submit(f, *args, **kwargs)

    return wrap


@threaded
def hb_solve_captcha_bsc(img_data):
    bcs_access_token = '3C30731306914373BED04F4C4FD4F1AA'
    bcs = BestCaptchaSolverAPI(bcs_access_token)
    if settings.DEBUG:
        balance = bcs.account_balance()
        logger.debug(f'BCS balance: {balance}')
    resp_id = bcs.submit_image_captcha(img_data)
    return bcs.retrieve(resp_id)


def hb_win_size(page, dim):
    S = lambda dim: page.execute_script('return document.body.parentNode.scroll' + dim)
    return S.__call__(dim) + 10


def hb_save_elem_screenshot(elem, txt='', force=False):
    if force or settings.SAVE_SCREENSHOTS:
        f_name = f'{settings.BASE_DIR}/logs/{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")}_{txt}_ess.png'
        logger.debug(f'Saving {f_name}')
        try:
            elem.screenshot(f_name)
        except Exception as e:
            logger.error(f'Could not save {f_name}: {e}')


def hb_save_page_screenshot(page, suffix, force=False):
    if force or settings.SAVE_SCREENSHOTS:
        page.set_window_size(hb_win_size(page, 'Width'), hb_win_size(page, 'Height'))
        f_name = f'{settings.BASE_DIR}/logs/{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")}_{suffix.lower()}_pss.png'
        logger.debug(f'Saving {f_name}')
        page.save_screenshot(f_name)


def hb_get_page_screenshot(page):
    page.set_window_size(hb_win_size(page, 'Width'), hb_win_size(page, 'Height'))
    return page.get_screenshot_as_base64()


def hb_save_failed_captcha(img, txt='NO CODE', force=False):
    if force or settings.SAVE_CAPTCHA:
        f_name = f'{settings.MEDIA_ROOT}/captcha/{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")}_{txt}_.png'
        logger.debug(f'Saving {f_name}')
        img.screenshot(f_name)


def hb_get_page(url):
    """
    Open Chrome via chromedriver, navigate to url and return t_load page
    :param url:
    :return: webdriver object
    """
    t_start = round(time(), 2)
    opts = ChromeOptions()
    opts.add_experimental_option('detach', True)
    opts.headless = settings.BROWSE_HEADLESS
    caps = DesiredCapabilities.CHROME.copy()
    caps['headless'] = settings.BROWSE_HEADLESS
    service_url = 'http://localhost:5780'
    browser = None
    if 'linux' in platform:
        # noinspection PyBroadException
        try:
            browser = Remote(command_executor=service_url, keep_alive=True, desired_capabilities=caps, options=opts)
            logger.info(f'Connected to chromedriver service on {service_url}')
        except:
            logger.error(f'Could not connect to chromedriver service on {service_url} : {exc_info()}, trying local Chrome...')

    if not browser:
        e_p = '/usr/bin/chromedriver' if 'linux' in platform else 'bin\\chromedriver.exe'
        # noinspection PyBroadException
        try:
            browser = Chrome(executable_path=e_p, desired_capabilities=caps, options=opts)
            logger.debug(f'Opened Chrome: {e_p}')
        except:
            msg = f'Could not open Chrome: {exc_info()}'
            logger.error(msg)
            return None, msg
    t_load = round(time(), 2)
    logger.debug(f'Browser t_load in {t_load - t_start} sec')

    # TODO: check the influence of maximizing
    #  while settings.BROWSE_HEADLESS = True

    # noinspection PyBroadException
    try:
        browser.maximize_window()
    except:
        logger.error(f'Can\'t maximize window: {exc_info()}')
        logger.error(f'Note: settings.BROWSE_HEADLESS={settings.BROWSE_HEADLESS}')

    try:
        browser.get(url)
    except TimeoutException as e:
        msg = f'Could not open {url}: {e}'
        logger.error(msg)
        return None, msg

    return browser, ''


def hb_set_value(trigger, num_input, value):
    """
    Look for node's child element, handling an exceptions.
    Retries 3 times, waiting 1 second.
    :param trigger:
    :param num_input:
    :param value:
    :return: (True, element object) if found and set or (False, error message) iotherwise
    """
    # total = 4
    total = 3
    # cnt = total - 1
    err_msg = ''
    while total:
        trigger.click()
        sleep(WAIT_05)
        total -= 1
        # noinspection PyBroadException
        try:
            num_input.clear()
            sleep(WAIT_01)
            num_input.send_keys(str(value))
        except ElementNotInteractableException as e:
            err_msg = e.msg
            continue
        except:
            err_msg = exc_info()[1].msg
            continue
        else:
            return True, err_msg

    return False, err_msg


def hb_select_value(wait, trigger, dd_xpath):
    """
    Look for node's child element, handling an exceptions.
    Retries 3 times, waiting 1 second.
    :param wait:
    :param trigger:
    :param dd_xpath:
    :return: (True, element object) if found and set or (False, error message) iotherwise
    """
    trigger.click()
    # noinspection PyBroadException
    try:
        option = wait.until(clickable((By.XPATH, dd_xpath)))
    except:
        err_msg = f'data:image/jpeg;base64,{trigger.screenshot_as_base64}'
    else:
        # noinspection PyBroadException
        try:
            option.click()
        except (ElementNotInteractableException, StaleElementReferenceException, TimeoutException) as e:
            err_msg = e.msg
        except:
            err_msg = f'data:image/jpeg;base64,{trigger.screenshot_as_base64}'
        else:
            return True, ''

    return False, err_msg


def hb_look_for(node, xpath):
    """
    Look for node's child element, handling an exceptions.
    Retries 3 times, waiting 1 second.
    :param node: node
    :param xpath: xpath to check
    :return: (True, element object) or (False, error message) if not found
    """
    # noinspection PyBroadException
    try:
        elem = node.find_element_by_xpath(xpath)
        return True, elem
    except (NoSuchElementException, StaleElementReferenceException) as e:
        err_msg = e.msg
    except:
        err_msg = exc_info()[1].msg

    if err_msg:
        logger.error(err_msg)
    return False, err_msg
