# HarBit Health insurance proposals view and result page parser.

from _.utils import *

logger = getLogger(__name__)

HEALTH_INPUT_URL = 'https://briut.cma.gov.il/Parameters'
HEALTH_OFFER_URL = 'https://briut.cma.gov.il/Parameters'
HEALTH_MAIN_FORM_XPATH = '//form[@id="uiParamsForm"]'
HEALTH_SUBMIT_BTN_XPATH = '//img[@id="uiCompareImage"]'
HEALTH_KILL_LIST = ','.join(
    ['header', 'footer', '.visible-xs', '.chartWrapp', '.paramsWraper', '#uiParamsForm', '#uiTitleDiv', '#uiResultsHeaderDiv', '#uiDivNoticeChart',
     '#uiBlueLabelDiv', '#uiLblResultCompare', '#uiFilterDiv'])
HEALTH_CVRG_SEL_XPATH = '//div[@id="uiInsuranceTypeInnerDiv"]//input[contains(@type,"checkbox")]'
HEALTH_MEDS_CHK_XPATH = '//input[@id="IsMedications"]'
HEALTH_SURG_CHK_XPATH = '//input[@id="IsSurgery"]'
HEALTH_IMPL_CHK_XPATH = '//input[@id="IsMedications"]'
HEALTH_NO_OFFERS_XPATH_REL = './div[@id="uiDivNoResults"]'
HEALTH_RESULT_ROW_XPATH = '//div[@id="uiResultsDiv"]/div[contains(@class,"listViewRow")]'
HEALTH_COMPANY_LINK_XPATH_REL = './div[contains(@class,"divLogo")]/div/a'
HEALTH_PRICE_XPATH_REL = './/div[contains(@class,"policyPriceCell")]/span'
HEALTH_SCORE_XPATH_REL = './/div[contains(@class,"scoreMeasureCell")]/span'
HEALTH_PARTS_LINK_XPAT_REL = './/a[contains(@class,"key-click")]'
HEALTH_PARTS_LIST_XPAT_REL = '//div[contains(@class,"thumbnail")]/div/*'
HEALTH_SURG_PREM_XPATH_REL = './/div[contains(@class,"toggleSurgeries")]//div[contains(@class,"pull-left")]/span[contains(@class,"thumbnail-title")]'
HEALTH_IMPL_PREM_XPATH_REL = './/div[contains(@class,"toggleImplants")]//div[contains(@class,"pull-left")]/span[contains(@class,"thumbnail-title")]'
HEALTH_MEDS_PREM_XPATH_REL = './/div[contains(@class,"toggleMedications")]//div[contains(@class,"pull-left")]/span[contains(@class,"thumbnail-title")]'
HEALTH_SURG_LIST_XPATH_REL = './/div[contains(@class,"toggleSurgeries")]//li/div'
HEALTH_IMPL_LIST_XPATH_REL = './/div[contains(@class,"toggleImplants")]//li/div'
HEALTH_MEDS_LIST_XPATH_REL = './/div[contains(@class,"toggleMedications")]//li/div'


def parse_row_health(row):
    """
    Parse result page for insurance proposals data, return data as object
    :param row
    :return: data object
    """
    page_data = {'msg': None, 'full': False}
    # wait_2s = WebDriverWait(page, 2)
    page_data['CompanyName'] = row.find_element_by_xpath(f'{HEALTH_COMPANY_LINK_XPATH_REL}/img').get_attribute('alt')
    logger.debug(f'----------Parsing row {page_data["CompanyName"]}...')
    page_data['LogoURL'] = row.find_element_by_xpath(f'{HEALTH_COMPANY_LINK_XPATH_REL}/img').get_attribute('src')
    page_data['ID'] = int(row.get_attribute('data-id'))
    page_data['URL'] = row.find_element_by_xpath(HEALTH_COMPANY_LINK_XPATH_REL).get_attribute('href')
    page_data['Price'] = int(row.find_element_by_xpath(HEALTH_PRICE_XPATH_REL).text[1:])
    page_data['ScoreMeasure'] = int(row.find_element_by_xpath(HEALTH_SCORE_XPATH_REL).text or '0')
    # incl_xpath = f'{HEALTH_RESULT_ROW_XPATH}[{idx}]{HEALTH_PARTS_LIST_XPAT_REL}'
    # more_info_btn = row.find_element_by_xpath(HEALTH_PARTS_LINK_XPAT_REL)
    # try:
    #     more_info_btn.click()
    # except (StaleElementReferenceException,
    #         ElementClickInterceptedException,
    #         ElementNotInteractableException) as e:
    #     err_msg = f'Not clickable (מה כולל הביטוח) at row {idx} : {e.msg}'
    #     logger.error(err_msg)
    #     # page_data['full'] = err_msg
    #     hb_save_page_screenshot(page, f'not_clickable_r{idx}')
    # else:
    #     # logger.debug(f'Waiting for {incl_xpath} to appear')
    #     try:
    #         wait_2s.until(all_visible((By.XPATH, incl_xpath)))
    #     except TimeoutException:
    #         logger.error(f'No extra data present for {page_data["CompanyName"]}!')
    #     else:
    page_data['SurgeriesMonthlyPremium'] = int(row.find_element_by_xpath(HEALTH_SURG_PREM_XPATH_REL).text.strip() or '-1')
    page_data['ImplantsMonthlyPremium'] = int(row.find_element_by_xpath(HEALTH_IMPL_PREM_XPATH_REL).text.strip() or '-1')
    page_data['MedicationsMonthlyPremium'] = int(row.find_element_by_xpath(HEALTH_MEDS_PREM_XPATH_REL).text.strip() or '-1')

    # [_.text for _ in row.find_elements_by_xpath(HEALTH_SURG_LIST_XPATH_REL)]
    page_data['SurgeriesBullets'] = []
    surg_bullets = row.find_elements_by_xpath(HEALTH_SURG_LIST_XPATH_REL)
    logger.debug(f'Found {len(surg_bullets)} surgery entries')
    for _ in surg_bullets:
        if _.text:
            page_data['SurgeriesBullets'].append(_.text)
    surg_missed = len(surg_bullets) - len(page_data['SurgeriesBullets'])
    if surg_missed:
        logger.error(f'Missed {surg_missed} surgery entries')

    # [_.text for _ in row.find_elements_by_xpath(HEALTH_IMPL_LIST_XPATH_REL)]
    page_data['ImplantsBullets'] = []
    impl_bullets = row.find_elements_by_xpath(HEALTH_IMPL_LIST_XPATH_REL)
    logger.debug(f'Found {len(impl_bullets)} implant entries')
    for _ in impl_bullets:
        if _.text:
            page_data['ImplantsBullets'].append(_.text)
    impl_missed = len(impl_bullets) - len(page_data['ImplantsBullets'])
    if impl_missed:
        logger.error(f'Missed {impl_missed} implant entries')

    # [_.text for _ in row.find_elements_by_xpath(HEALTH_MEDS_LIST_XPATH_REL)]
    page_data['MedicationsBullets'] = []
    medi_bullets = row.find_elements_by_xpath(HEALTH_MEDS_LIST_XPATH_REL)
    logger.debug(f'Found {len(medi_bullets)} medicate entries')
    for _ in medi_bullets:
        if _.text:
            page_data['MedicationsBullets'].append(_.text)
    medi_missed = len(medi_bullets) - len(page_data['MedicationsBullets'])
    if medi_missed:
        logger.error(f'Missed {medi_missed} medicate entries')

    if not surg_missed and not impl_missed and not medi_missed:
        page_data['full'] = True
    del page_data['msg']

    return page_data


def parse_page_health(page, own_client):
    """
    Parse result page for insurance proposals data, return data as object
    :param page: selenium webdriver object
    :param own_client: own GUI flag
    :return: data object
    """
    sleep(WAIT_05)
    wait_120s = WebDriverWait(page, 120)
    response = {'data': None, 'msg': '', }
    page.execute_script(JS_SCROLL_DOWN)
    try:
        wait_120s.until(present((By.XPATH, HEALTH_RESULT_ROW_XPATH)))
    except TimeoutException:
        err_msg = 'No result rows found!'
        response.update({'msg': err_msg})
        logger.error(err_msg)
        hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_rows')
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_no_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
    else:
        page.execute_script(f'document.querySelectorAll("{HEALTH_KILL_LIST}").forEach(function(element) {{element.remove();}})')
        page.execute_script(JS_SCROLL_DOWN)
        page.set_window_size(hb_win_size(page, 'Width'), hb_win_size(page, 'Height'))
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_parsing')
        result_rows = page.find_elements_by_xpath(HEALTH_RESULT_ROW_XPATH)

        if result_rows:
            msg = f'{len(result_rows)} data rows found'
            response.update({'data': [], 'msg': msg})
            logger.debug(msg)
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            retry_rows = []
            result_rows.reverse()
            parse_cnt = 3
            while parse_cnt and result_rows:
                if retry_rows:
                    logger.debug(f'Retrying {len(retry_rows)} missed rows')
                    result_rows = retry_rows
                    retry_rows = []
                rows_left = len(result_rows)
                logger.debug(f'Pass {4 - parse_cnt}, {rows_left} rows to parse')
                if own_client:
                    hb_save_page_screenshot(page, f'pass_{4 - parse_cnt}')

                for idx, row in enumerate(result_rows):
                    r = row.find_element_by_xpath(HEALTH_PARTS_LINK_XPAT_REL)
                    # page['data'].append({'ID': r.get_attribute('data-id')})
                    sleep(WAIT_01)
                    try:
                        r.click()
                    except ElementClickInterceptedException as e:
                        err_msg = f'Row {rows_left - idx} not clickable: {e}'
                        logger.error(err_msg)
                        if own_client:
                            hb_save_elem_screenshot(row, f'not_clickable_{rows_left - idx}')

                for idx, row in enumerate(result_rows):
                    row_ind = rows_left - idx
                    if own_client:
                        hb_save_elem_screenshot(row, f'row_{row_ind}')
                    row_data = parse_row_health(row)
                    if not row_data['full']:
                        logger.error(f'Row {row_ind} not full, shoud retry: {row_data}')
                        retry_rows.append(row)
                        if own_client:
                            hb_save_elem_screenshot(row, f'not_full_{row_ind}')
                    else:
                        if 'msg' not in row_data.keys():
                            del row_data['full']
                            response['data'].append(row_data)  # del result_rows[idx]
                if len(retry_rows):
                    parse_cnt -= 1
                else:
                    break

            response.update({'msg': 'Ok'})
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_result': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_result')

    page.quit()
    return response


def health_view(request):
    """
    Collect data from Health Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'health'})

    # take from request
    req_body = request.body.decode()
    logger.debug(f'Received content: {req_body}')
    req_obj = json.loads(req_body)
    birth_date = req_obj.get('Age')
    gender = 'FM'.index(req_obj.get('Gender'))
    own_client = bool(req_obj.get('own_client'))
    # surgery = bool(req_obj.get('Operations'))
    # implants = bool(req_obj.get('Transplant'))
    # meds = bool(req_obj.get('Medicine'))
    # all_types = True

    t_start = round(time(), 2)
    page, err = hb_get_page(HEALTH_INPUT_URL)
    t_load = round(time(), 2)
    response = {'data': None, 'msg': err, }
    logger.debug(f'Page loaded in {t_load - t_start} sec')
    if page:
        wait_30s = WebDriverWait(page, 30)

        try:
            wait_30s.until(clickable((By.XPATH, HEALTH_MAIN_FORM_XPATH)))
        except TimeoutException:
            err_msg = f'Not clickable at "{HEALTH_MAIN_FORM_XPATH}"'
            response.update({'msg': err_msg})
            logger.error(err_msg)
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_clickable')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_not_clickable': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
        else:

            """
            סוגי כיסויי
            """
            # if meds or all_types:
            #     page.find_element_by_xpath(HEALTH_MEDS_CHK_XPATH).click()
            #
            # if surgery or all_types:
            #     page.find_element_by_xpath(HEALTH_SURG_CHK_XPATH).click()
            #
            # if implants or all_types:
            #     page.find_element_by_xpath(HEALTH_IMPL_CHK_XPATH).click()
            [ins_type.click() for ins_type in page.find_elements_by_xpath(HEALTH_CVRG_SEL_XPATH)]
            logger.debug('Set סוגי כיסויי')

            """
            מין
            """
            gender_inputs = page.find_elements_by_xpath('//div[contains(@class,"k-slider-buttons")]/a')
            gender_inputs[gender].click()
            logger.debug(f'Set מין to {gender}')

            """
            תאריך לידה
            """
            try:
                wait_30s.until(clickable((By.XPATH, '//input[@id="uiTxtAge"]')))
            except TimeoutException:
                logger.error(f'Main form not clickable at {HEALTH_MAIN_FORM_XPATH}')
                response.update({'msg': 'Main form not clickable'})
                if own_client:
                    response.update({f'{page.current_url.split("=")[-1]}_not_clickable': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
                    hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_clickable')
            else:

                birthdate_input = page.find_element_by_xpath('//input[@id="uiTxtAge"]')
                if birthdate_input:
                    # if own_client:
                    #     response.update({'bd_before': f'data:image/jpeg;base64,{birthdate_input.screenshot_as_base64}'})
                    bith_year = f'01/01/{birth_date.split("/")[-1]}'
                    # birthdate_input.click()
                    birthdate_input.send_keys(bith_year)
                    logger.debug(
                        f'Set תאריך לידה to {birth_date}')  # if own_client:  #     response.update({'bd_after': f'data:image/jpeg;base64,{birthdate_input.screenshot_as_base64}'})
                else:
                    response.update({'msg': 'No BD input!'})

            page.find_element_by_xpath(HEALTH_SUBMIT_BTN_XPATH).click()

            t_submit = round(time(), 2)
            logger.debug(f'Controls set in {t_submit - t_load} sec')

            response.update(parse_page_health(page, own_client))
            t_parse = round(time(), 2)
            logger.info(f'Page t_parse in {t_parse - t_submit} sec')

    return JsonResponse(response)
