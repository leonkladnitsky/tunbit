# HarBit appartment related:
# Building, Content, Full property insurance proposals views
# and shared Appartment result page parser.

from _.utils import *

logger = getLogger(__name__)

CONTENT_INPUT_URL = 'https://dira.cma.gov.il/Home/FillParameters?InsuranceType=Content'
BUILDING_INPUT_URL = 'https://dira.cma.gov.il/Home/FillParameters?InsuranceType=Structure'
FULLPROP_INPUT_URL = 'https://dira.cma.gov.il/Home/FillParameters?InsuranceType=StructureAndContent'
APPT_OFFER_URL = 'https://dira.cma.gov.il/CalcResults/CalcResults'
APPT_DD_CONTROL_XPATH = '//span[contains(@class,"k-widget") and contains(@class,"k-dropdown") and contains(@class,"k-header")]'
APPT_RESULT_ROW_XPATH = '//div[@id="uiGridResults"]/div[contains(@class,"k-grid-content")]/table/tbody/tr[contains(@class,"k-master-row")]'
APPT_MAIN_CELL_XPATH_REL = '/td/table/tbody/tr/td[2]'
APPT_COMPANY_LINK_XPATH_REL = '/span[contains(@class,"corp-logo")]/a'
APPT_TITLE_XPATH_REL = '/label[contains(@class,"grid-first-row")]'
APPT_RATING_XPATH_REL = '/span/a[contains(@class,"numTxtcolor") and contains(@class,"hidden-xs")]'
APPT_PRICE_XPATH_REL = '/span[contains(@class,"resultsTxtcolor") and contains(@class,"hidden-xs")]'
APPT_SUBMIT_BTN_XPATH = '//button[@id="uiBtnCalculate"]'


def parse_page_appt(page, own_client):
    """
    Parse result page for appt insurance proposals data, return data as object
    :param page: selenium webdriver object
    :param own_client: own GUI flag
    :return: data object
    """
    response = {'data': None, 'msg': '', }
    page.implicitly_wait(WAIT_SEC)
    page.execute_script(JS_SCROLL_DOWN)
    wait_30s = WebDriverWait(page, 30)
    try:
        wait_30s.until(all_visible((By.XPATH, APPT_RESULT_ROW_XPATH)))
    except TimeoutException as e:
        logger.error(f'{e}')
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_result_rows')
        return {'data': [], 'msg': f'{e}', }
    else:
        result_rows = page.find_elements_by_xpath(APPT_RESULT_ROW_XPATH)

    if result_rows:
        msg = f'{len(result_rows)} data rows found'
        response.update({'data': [], 'msg': msg})
        logger.debug(msg)
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows')
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
        for idx, row in enumerate(result_rows):
            main_cell_xpath = f'{APPT_RESULT_ROW_XPATH}[{idx + 1}]{APPT_MAIN_CELL_XPATH_REL}'
            # logger.debug(f'Finding {main_cell_xpath}')
            # main_cell = None
            # try:
            #     wait.until(clickable((By.XPATH, main_cell_xpath)))
            # except TimeoutException as e:
            #     err_msg = f'TimeoutException: {e}\nNot clickable: {main_cell_xpath}'
            #     logger.error(err_msg)
            # else:
            try:
                page.find_element_by_xpath(main_cell_xpath)
            except NoSuchElementException as e:
                logger.error(f'No main_cell: {main_cell_xpath}: {e.msg}')
                break

            page_data = {}

            link_xpath = main_cell_xpath + APPT_COMPANY_LINK_XPATH_REL
            # link = None
            # try:
            #     wait.until(clickable((By.XPATH, link_xpath)))
            # except TimeoutException as e:
            #     err_msg = f'TimeoutException: {e}\nNot clickable: {link_xpath}'
            #     logger.error(err_msg)
            # else:
            try:
                link = page.find_element_by_xpath(link_xpath)
            except NoSuchElementException as e:
                logger.error(f'No link: {link_xpath}: {e.msg}')
            else:
                page_data['company_url'] = link.get_attribute('href')
                page_data['company_name'] = link.get_attribute('title').split(' , ')[0]
            # else:
            #     logger.error(f'link_not_found in row {idx+1}')

            title_xpath = main_cell_xpath + APPT_TITLE_XPATH_REL
            # title = None
            # try:
            #     wait.until(clickable((By.XPATH, title_xpath)))
            # except TimeoutException as e:
            #     err_msg = f'TimeoutException: {e}\nNot clickable: {title_xpath}'
            #     logger.error(err_msg)
            # else:
            try:
                title = page.find_element_by_xpath(title_xpath)
            except NoSuchElementException as e:
                logger.error(f'No title {title_xpath}: {e.msg}')
            else:
                page_data['title'] = title.text
            # else:
            #     logger.error(f'title_not_found in row {idx+1}')

            rating_xpath = main_cell_xpath + APPT_RATING_XPATH_REL
            # rating = None
            # try:
            #     wait.until(clickable((By.XPATH, rating_xpath)))
            # except TimeoutException as e:
            #     err_msg = f'TimeoutException: {e}\nNot clickable: {rating_xpath}'
            #     logger.error(err_msg)
            # else:
            try:
                rating = page.find_element_by_xpath(rating_xpath)
            except NoSuchElementException as e:
                logger.error(f'Not found {rating_xpath}: {e.msg}')
            else:
                page_data['rating'] = rating.text
            # else:
            #     logger.error(f'rating_not_found in row {idx+1}')

            price_xpath = main_cell_xpath + APPT_PRICE_XPATH_REL
            # price = None
            # try:
            #     wait.until(clickable((By.XPATH, price_xpath)))
            # except TimeoutException as e:
            #     err_msg = f'TimeoutException: {e}\nNot clickable: {price_xpath}'
            #     logger.error(err_msg)
            # else:
            try:
                price = page.find_element_by_xpath(price_xpath)
            except NoSuchElementException as e:
                logger.error(f'Not found {price_xpath}: {e.msg}')
            else:
                page_data['ins_price'] = price.text  # logger.error(f'price_not_found in row {idx+1}')

            response['data'].append(page_data)  # logger.debug(f'Row data: {page_data}")
    else:
        err_msg = 'No result rows found!'
        response.update({'msg': err_msg})
        logger.error(err_msg)
        hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_rows')
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_no_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
    page.quit()
    return response


def content_view(request):
    """
    Collect data from Content Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'content'})

    # take from request
    req_body = request.body.decode()
    logger.debug(f'Request: {req_body}')
    req_obj = json.loads(req_body)
    c_type_floor = req_obj.get('c_type_floor', 0)
    c_mid_floor = req_obj.get('c_mid_floor', 0)
    c_ins_sum = req_obj.get('c_ins_sum', 0)
    c_prev_claims = req_obj.get('c_prev_claims', 0)
    own_client = bool(req_obj.get('own_client'))

    t_start = round(time(), 2)
    page, err = hb_get_page(CONTENT_INPUT_URL)
    wait_5s = WebDriverWait(page, 5)
    response = {'data': None, 'msg': err, }
    wait_5s.until(clickable((By.XPATH, '//form[@id="uiFormParameters"]')))
    t_load = round(time(), 2)
    logger.debug(f'Page loaded in {t_load - t_start} sec')
    if page:
        """
        סוג מבנה וקומה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlStructureAndFloorType_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlStructureAndFloorType_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set סוג מבנה וקומה')
        else:
            select_options[int(c_type_floor)].click()
            page.implicitly_wait(WAIT_001)

        """
        תביעות
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlNumberOfContentClaims_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlNumberOfContentClaims_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set תביעות')
        else:
            select_options[int(c_prev_claims)].click()
            page.implicitly_wait(WAIT_001)

        """
        סכום
        """
        txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNContentInsuranceSum"]/../..')
        txt_trigger.click()
        try:
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNContentInsuranceSum"]')))
        except TimeoutException:
            logger.error('Could not set סכום')
        else:
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(c_ins_sum))
            page.implicitly_wait(WAIT_001)

        """
        קומת ביניים
        """
        if c_type_floor in ['4', 4]:
            txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNMidFloor"]/../..')
            txt_trigger.click()
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNMidFloor"]')))
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(c_mid_floor))
            page.implicitly_wait(WAIT_001)

        submit_btn = page.find_element_by_xpath(APPT_SUBMIT_BTN_XPATH)
        submit_btn.click()
        t_submit = round(time(), 2)
        logger.debug(f'Controls set in {t_submit - t_load} sec')
        try:
            wait_5s.until(url_matches(APPT_OFFER_URL))
        except TimeoutException:
            err_msg = f'No url match for "{APPT_OFFER_URL}"'
            response.update({'msg': err_msg})
            logger.error(err_msg)
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_wrong_url')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_wrong_url': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
        else:
            try:
                wait_5s.until(clickable((By.XPATH, APPT_DD_CONTROL_XPATH)))
            except TimeoutException:
                err_msg = f'Not clickable at "{APPT_DD_CONTROL_XPATH}"'
                response.update({'msg': err_msg})
                logger.error(err_msg)
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_clickable')
                if own_client:
                    response.update({f'{page.current_url.split("=")[-1]}_not_clickable': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            else:
                response.update(parse_page_appt(page, own_client))
                t_parse = round(time(), 2)
                logger.debug(f'Results t_parse in {t_parse - t_submit} sec')
                logger.info(f'Page total in {t_parse - t_start} sec')
    return JsonResponse(response)


def building_view(request):
    """
    Collect data from Building Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'building'})

    # take from request
    req_body = request.body.decode()
    logger.debug(f'Request: {req_body}')
    req_obj = json.loads(req_body)
    b_type_floor = req_obj.get('b_type_floor', 0)
    b_mid_floor = req_obj.get('b_mid_floor', 0)
    b_age = req_obj.get('b_age', 0)
    b_water_coverage = req_obj.get('b_water_coverage', 0)
    b_ins_sum = req_obj.get('b_ins_sum', 0)
    b_prev_claims = req_obj.get('b_prev_claims', 0)
    b_mortgage = req_obj.get('b_mortgage', 0)
    own_client = bool(req_obj.get('own_client'))

    t_start = round(time(), 2)
    page, err = hb_get_page(BUILDING_INPUT_URL)
    wait_5s = WebDriverWait(page, 5)
    response = {'data': None, 'msg': err, }
    wait_5s.until(clickable((By.XPATH, '//form[@id="uiFormParameters"]')))
    t_load = round(time(), 2)
    logger.debug(f'Page loaded in {t_load - t_start} sec')
    if page:
        """
        סוג מבנה וקומה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlStructureAndFloorType_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlStructureAndFloorType_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set סוג מבנה וקומה')
        else:
            select_options[int(b_type_floor)].click()
            page.implicitly_wait(WAIT_001)

        """
        תביעות
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlNumberOfStructureClaims_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlNumberOfStructureClaims_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set תביעות')
        else:
            select_options[int(b_prev_claims)].click()
            page.implicitly_wait(WAIT_001)

        """
        נזקי מים
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlFluidDangerCoverage_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlFluidDangerCoverage_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set נזקי מים')
        else:
            select_options[int(b_water_coverage)].click()
            page.implicitly_wait(WAIT_001)

        """
        משכנתה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlMortgage_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlMortgage_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set משכנתה')
        else:
            select_options[int(b_mortgage)].click()
            page.implicitly_wait(WAIT_001)

        """
        סכום
        """
        txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNStructureInsuranceSum"]/../..')
        txt_trigger.click()
        try:
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNStructureInsuranceSum"]')))
        except TimeoutException:
            logger.error('Could not set סכום')
        else:
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(b_ins_sum))
            page.implicitly_wait(WAIT_001)

        """
        גיל המבנה
        """
        txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNAge"]/../..')
        txt_trigger.click()
        try:
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNAge"]')))
        except TimeoutException:
            logger.error('Could not set סכום')
        else:
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(b_age))
            page.implicitly_wait(WAIT_001)

        """
        קומת ביניים
        """
        if b_type_floor in ['4', 4]:
            txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNMidFloor"]/../..')
            txt_trigger.click()
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNMidFloor"]')))
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(b_mid_floor))
            page.implicitly_wait(WAIT_001)

        submit_btn = page.find_element_by_xpath(APPT_SUBMIT_BTN_XPATH)
        submit_btn.click()
        t_submit = round(time(), 2)
        logger.debug(f'Controls set in {t_submit - t_load} sec')

        try:
            wait_5s.until(url_matches(APPT_OFFER_URL))
        except TimeoutException:
            err_msg = f'No url match for "{APPT_OFFER_URL}"'
            response.update({'msg': err_msg, 'url': page.current_url})
            logger.error(err_msg)
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_wrong_url')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_wrong_url': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
        else:
            try:
                wait_5s.until(clickable((By.XPATH, APPT_DD_CONTROL_XPATH)))
            except TimeoutException:
                err_msg = f'Not clickable at "{APPT_DD_CONTROL_XPATH}"'
                response.update({'msg': err_msg})
                logger.error(err_msg)
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_clickable')
                if own_client:
                    response.update({f'{page.current_url.split("=")[-1]}_not_clickable': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            else:
                response.update(parse_page_appt(page, own_client))
                t_parse = round(time(), 2)
                logger.debug(f'Results t_parse in {t_parse - t_submit} sec')
                logger.info(f'Page total in {t_parse - t_start} sec')
    return JsonResponse(response)


def fullprop_view(request):
    """
    Collect data from Full property Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'fullprop'})

    # take from request
    req_body = request.body.decode()
    logger.debug(f'Request: {req_body}')
    req_obj = json.loads(req_body)
    f_type_floor = req_obj.get('f_type_floor', 0)
    fb_mid_floor = req_obj.get('fb_mid_floor', 0)
    fb_age = req_obj.get('fb_age', 0)
    f_water_coverage = req_obj.get('f_water_coverage', 0)
    f_mortgage = req_obj.get('f_mortgage', 0)
    fb_ins_sum = req_obj.get('fb_ins_sum', 0)
    fb_prev_claims = req_obj.get('fb_prev_claims', 0)
    fc_ins_sum = req_obj.get('fc_ins_sum', 0)
    fc_prev_claims = req_obj.get('fc_prev_claims', 0)
    own_client = bool(req_obj.get('own_client'))

    t_start = round(time(), 2)
    page, err = hb_get_page(FULLPROP_INPUT_URL)
    wait_5s = WebDriverWait(page, 5)
    response = {'data': None, 'msg': err, }
    wait_5s.until(clickable((By.XPATH, '//form[@id="uiFormParameters"]')))
    t_load = round(time(), 2)
    logger.debug(f'Page loaded in {t_load - t_start} sec')
    if page:
        """
        סוג מבנה וקומה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlStructureAndFloorType_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlStructureAndFloorType_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set סוג מבנה וקומה')
        else:
            select_options[int(f_type_floor)].click()  # page.implicitly_wait(WAIT_XS)

        """
        תביעות תכולה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlNumberOfContentClaims_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlNumberOfContentClaims_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set תביעות תכולה')
        else:
            select_options[int(fc_prev_claims)].click()  # page.implicitly_wait(WAIT_XS)

        """
        תביעות מבנה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlNumberOfStructureClaims_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlNumberOfStructureClaims_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set תביעות מבנה')
        else:
            select_options[int(fb_prev_claims)].click()  # page.implicitly_wait(WAIT_XS)

        """
        נזקי מים
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlFluidDangerCoverage_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlFluidDangerCoverage_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set נזקי מים')
        else:
            select_options[int(f_water_coverage)].click()  # page.implicitly_wait(WAIT_XS)

        """
        משכנתה
        """
        select_trigger = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlMortgage_listbox")]')
        select_trigger.click()
        try:
            select_options = wait_5s.until(all_visible((By.XPATH, '//ul[@id="uiDdlMortgage_listbox"]/li')))
        except TimeoutException:
            logger.error('Could not set משכנתה')
        else:
            select_options[int(f_mortgage)].click()  # page.implicitly_wait(WAIT_XS)

        """
        סכום תכולה
        """
        txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNStructureInsuranceSum"]/../..')
        txt_trigger.click()
        try:
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNStructureInsuranceSum"]')))
        except TimeoutException:
            logger.error('Could not set סכום תכולה')
        else:
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(fb_ins_sum))  # page.implicitly_wait(WAIT_XS)

        """
        סכום מבנה
        """
        txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNContentInsuranceSum"]/../..')
        txt_trigger.click()
        try:
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNContentInsuranceSum"]')))
        except TimeoutException:
            logger.error('Could not set סכום מבנה')
        else:
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(fc_ins_sum))  # page.implicitly_wait(WAIT_XS)

        """
        גיל המבנה
        """
        txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNAge"]/../..')
        txt_trigger.click()
        try:
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNAge"]')))
        except TimeoutException:
            logger.error('Could not set גיל המבנה')
        else:
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(fb_age))  # page.implicitly_wait(WAIT_XS)

        """
        קומת ביניים
        """
        if f_type_floor in ['4', 4]:
            txt_trigger = page.find_element_by_xpath('//input[@id="uiTxtNMidFloor"]/../..')
            txt_trigger.click()
            txt_input = wait_5s.until(clickable((By.XPATH, '//input[@id="uiTxtNMidFloor"]')))
            txt_input.clear()
            sleep(WAIT_01)
            txt_input.send_keys(str(fb_mid_floor))  # page.implicitly_wait(WAIT_XS)

        submit_btn = page.find_element_by_xpath(APPT_SUBMIT_BTN_XPATH)
        submit_btn.click()
        t_submit = round(time(), 2)
        logger.debug(f'Controls set in {t_submit - t_load} sec')

        try:
            wait_5s.until(url_matches(APPT_OFFER_URL))
        except TimeoutException:
            err_msg = f'No url match for "{APPT_OFFER_URL}"'
            response.update({'msg': err_msg, 'url': page.current_url})
            logger.error(err_msg)
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_wrong_url')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_wrong_url': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
        else:
            try:
                wait_5s.until(clickable((By.XPATH, APPT_DD_CONTROL_XPATH)))
            except TimeoutException:
                err_msg = f'Not clickable at "{APPT_DD_CONTROL_XPATH}"'
                response.update({'msg': err_msg})
                logger.error(err_msg)
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_clickable')
                if own_client:
                    response.update({f'{page.current_url.split("=")[-1]}_not_clickable': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            else:
                response.update(parse_page_appt(page, own_client))
                t_parse = round(time(), 2)
                logger.debug(f'Results t_parse in {t_parse - t_submit} sec')
                logger.info(f'Page total in {t_parse - t_start} sec')
    return JsonResponse(response)
