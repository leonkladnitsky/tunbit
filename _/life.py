# HarBit Life insurance proposals view and result page parser.

from _.utils import *

logger = getLogger(__name__)

LIFE_INPUT_URL = 'https://life.cma.gov.il/RiskParameters/RiskParameters?id=84300001'
LIFE_OFFER_URL = 'https://life.cma.gov.il/RiskParameters/RiskParameters?id=84300001'
LIFE_SUBMIT_BTN_XPATH = '//a[@id="uiBtnCalc"]'
LIFE_NO_OFFERS_XPATH_REL = './div[@id="uiDivNoResults]'
LIFE_RESULT_ROW_XPATH = '//div[@id="uiResultsDiv"]/div[contains(@class,"rowWrapp")]'
LIFE_KILL_LIST = ','.join(
    ['header', 'footer', '.visible-xs', '.title-wrap', '#graphInfoX', '#kk', '#uiParameters', '#uiGeneralRemarksDiv', '#uiResultsHeaderDiv', '#uiNoticeDiv',
     '#resultsHeader', '.chartWrapp', 'br', 'hr', '#graphStep'])
LIFE_COMPANY_LINK_XPATH_REL = './div[1]/a'
LIFE_NO_OFFER_XPATH_REL = './div[contains(@class,"notOffer")]'
LIFE_1ST_PREM_XPATH_REL = './div[2]'
LIFE_AVG_PREM_XPATH_REL = './div[3]'
LIFE_TOT_PREM_XPATH_REL = './div[4]'
LIFE_COMMENT_XPATH_REL = './div[5]/div'
LIFE_CHART_XPATH = '//div[@id="uiChartDiv"]'
LIFE_GRPH_INFO_XPATH = '//div[@id="graphInfo"]'
LIFE_GRPH_DATA_ATTR = 'data-graphresults'


def parse_page_life(page, own_client):
    """
    Parse result page for insurance proposals data, return data as object
    :param page: selenium webdriver object
    :param own_client: own GUI flag
    :return: data object
    """
    wait_120s = WebDriverWait(page, 120)
    page.execute_script(JS_SCROLL_DOWN)
    response = {'data': None, 'msg': '', }
    try:
        wait_120s.until(present((By.XPATH, LIFE_RESULT_ROW_XPATH)))
    except TimeoutException:
        err_msg = 'No data div present!'
        response.update({'msg': err_msg})
        logger.error(err_msg)
        hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_data', True)
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_no_data_div': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
    else:
        page.execute_script(f'document.querySelectorAll("{LIFE_KILL_LIST}").forEach(function(element) {{element.remove();}})')
        page.execute_script(JS_SCROLL_DOWN)
        page.set_window_size(hb_win_size(page, 'Width'), hb_win_size(page, 'Height'))
        # sleep(WAIT_01)
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_parsing')
        result_rows = page.find_elements_by_xpath(LIFE_RESULT_ROW_XPATH)
        response = {'data': None, 'msg': '', }
        if result_rows:
            msg = f'{len(result_rows)} data rows found'
            response.update({'data': [], 'msg': msg})
            logger.debug(msg)
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            for idx, row in enumerate(result_rows):
                page_data = {}

                link = row.find_element_by_xpath(LIFE_COMPANY_LINK_XPATH_REL)
                page_data['Link'] = link.get_attribute('href')
                page_data['CompanyName'] = link.find_element_by_xpath('./img').get_attribute('alt')
                try:
                    row.find_element_by_xpath(LIFE_NO_OFFER_XPATH_REL)
                except NoSuchElementException:
                    first_prem = row.find_element_by_xpath(LIFE_1ST_PREM_XPATH_REL).text.replace(',', '')
                    avg_prem = row.find_element_by_xpath(LIFE_AVG_PREM_XPATH_REL).text.replace(',', '')
                    tot_prem = row.find_element_by_xpath(LIFE_TOT_PREM_XPATH_REL).text.replace(',', '')
                    comment = row.find_element_by_xpath(LIFE_COMMENT_XPATH_REL).get_attribute('onclick').split('\'')[1]
                    comments = f'https://life.cma.gov.il/{comment}'
                else:
                    first_prem = '0'
                    avg_prem = '0'
                    tot_prem = '0'
                    comments = '0'

                page_data['First'] = first_prem
                page_data['Average'] = avg_prem
                page_data['Accumulative'] = tot_prem
                page_data['Comments'] = ''  # comments
                response['data'].append(page_data)
            try:
                data_div = wait_120s.until(present((By.XPATH, LIFE_GRPH_INFO_XPATH)))
            except TimeoutException:
                err_msg = 'No chart info present!'
                response.update({'msg': err_msg})
                logger.error(err_msg)
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_info')
                if own_client:
                    response.update({f'{page.current_url.split("=")[-1]}_no_info': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            else:
                chart_data = json.loads(data_div.get_attribute(LIFE_GRPH_DATA_ATTR))
                logger.debug(f'Found {len(chart_data)} data items.')

                for item in response['data']:
                    for jdx in chart_data:
                        # noinspection PyTypeChecker
                        if jdx['CompanyName'] == item['CompanyName']:
                            item['MonthlyPremiumsDec'] = jdx['MonthlyPremiumsDec']
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_result': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_result')
        else:
            err_msg = 'No result rows found!'
            response.update({'msg': err_msg})
            logger.error(err_msg)
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_rows')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_no_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
    page.quit()
    return response


def life_view(request):
    """
    Collect data from Life Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'life'})

    # take from request
    req_body = request.body.decode()
    logger.debug(f'Received content: {req_body}')
    req_obj = json.loads(req_body)
    PremiumType = int(req_obj.get('PremiumType', '1'))
    DesiredPeriod = req_obj.get('DesiredPeriod', '0')
    DesiredSum = req_obj.get('DesiredSum', '0')
    BirthDate = req_obj.get('BirthDate')
    Gender = int(req_obj.get('Gender'))
    IsSmoking = int(req_obj.get('IsSmoking'))
    own_client = bool(req_obj.get('own_client'))

    t_start = round(time(), 2)
    page, err = hb_get_page(LIFE_INPUT_URL)
    response = {'data': None, 'msg': err, }
    wait_5s = WebDriverWait(page, 5)
    wait_5s.until(clickable((By.XPATH, '//form[@id="uiFormParameters"]')))
    t_load = round(time(), 2)
    logger.debug(f'Page loaded in {t_load - t_start} sec')
    if page:
        logger.debug(f'Setting controls...')

        """
        סוג הפרמיה
        """
        pt_action = ActionChains(page)
        pt_ctrl = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlPremiumType_listbox")]')
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_click_PT')
        pt_ctrl.click()
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_click_PT')
        pt_sel = page.find_element_by_xpath(f'//ul[@id="uiDdlPremiumType_listbox"]/li[{PremiumType}]')
        pt_action.move_to_element(pt_sel)
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_select_PT')
        pt_action.perform()
        pt_sel.click()
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_select_PT')

        """
        תאריך לידה
        """
        bd_inp = page.find_element_by_xpath(f'//input[@id="uiTxtAge1"]')
        ins_BD = f'01/01/{BirthDate.split("/")[-1]}'
        gender_ndx = int(Gender)
        ins_GN = ['Male', 'Female'][gender_ndx]
        smoke_ndx = int(IsSmoking)
        ins_IS = ['Yes', 'No'][smoke_ndx]
        logger.debug(f'BirthDate: {ins_BD}({BirthDate}), Gender: {ins_GN}({Gender}), IsSmoking: {ins_IS}({IsSmoking})')
        bd_inp.clear()
        sleep(WAIT_01)
        bd_inp.send_keys(ins_BD)

        """
        מין המבוטח
        """
        # try with exceptions
        gender_btn = page.find_element_by_xpath(f'//label[contains(@for,"uiRd{ins_GN}1")]')
        gender_btn.click()

        """
        עישון
        """
        # try with exceptions
        smoke_btn = page.find_element_by_xpath(f'//label[contains(@for,"uiRdSmoke{ins_IS}1")]')
        smoke_btn.click()

        """
        תקופת ביטוח
        """
        page.find_element_by_xpath(f'//input[contains(@id,"uiLDesiredPeriod")]/preceding-sibling::input').click()
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_send_DP')
        # noinspection PyBroadException
        try:
            page.find_element_by_xpath(f'//input[contains(@id,"uiLDesiredPeriod")]').send_keys(DesiredPeriod)
            sleep(WAIT_05)
        except:
            err_msg = 'Could not set תקופת ביטוח!'
            logger.error(err_msg)
            response.update({'msg': err_msg})
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_sent_DP')
            return -1, response
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_send_DP')

        """
        סכום ביטוח
        """
        page.find_element_by_xpath(f'//input[contains(@id,"uiLDesiredSum")]/preceding-sibling::input').click()
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_send_DS')
        # noinspection PyBroadException
        try:
            page.find_element_by_xpath(f'//input[contains(@id,"uiLDesiredSum")]').send_keys(DesiredSum)
            sleep(WAIT_05)
        except:
            err_msg = 'Could not set סכום ביטוח!'
            logger.error(err_msg)
            response.update({'msg': err_msg})
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_sent_DS')
            return -1, response
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_send_DS')

        page.find_element_by_xpath(LIFE_SUBMIT_BTN_XPATH).click()
        # sleep(5 * WAIT_SEC)
        t_submit = round(time(), 2)
        logger.debug(f'Controls set in {t_submit - t_load} sec')
        response.update(parse_page_life(page, own_client))
        t_parse = round(time(), 2)
        logger.info(f'Page t_parse in {t_parse - t_submit} sec')
    return JsonResponse(response)
