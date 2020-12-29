# HarBit Mortgage insurance proposals view and result page parser.

from _.utils import *

logger = getLogger(__name__)

MORT_INPUT_URL = 'https://life.cma.gov.il/RiskParameters/RiskParameters?id=84300003'
MORT_OFFER_URL = 'https://life.cma.gov.il/RiskParameters/RiskParameters?id=84300003'
MORT_SUBMIT_BTN_XPATH = '//a[@id="uiBtnCalc"]'
MORT_RESULT_ROWS_XPATH = '//div[@id="uiResultsDiv"]/div[contains(@class,"rowWrapp")]'
MORT_KILL_LIST = ','.join(
    ['header', 'footer', '.visible-xs', '.title-wrap', '#graphInfoX', '#kk', '#uiParameters', '#uiGeneralRemarksDiv', '#uiResultsHeaderDiv', '#uiNoticeDiv',
     '#resultsHeader', '.chartWrapp', 'br', 'hr', '#graphStep'])
MORT_COMPANY_LINK_XPATH_REL = './div[1]/a'
MORT_NO_OFFER_XPATH_REL = './div[contains(@class,"notOffer")]'
MORT_1ST_PREM_XPATH_REL = './div[2]'
MORT_AVG_PREM_XPATH_REL = './div[3]'
MORT_TOT_PREM_XPATH_REL = './div[4]'
MORT_COMMENT_XPATH_REL = './div[5]/div'
MORT_CHART_XPATH = '//div[@id="uiChartDiv"]'
MORT_GRPH_INFO_XPATH = '//div[@id="graphInfo"]'
MORT_GRPH_DATA_ATTR = 'data-graphresults'


def parse_page_mortgage(page, own_client):
    """
    Parse result page for insurance proposals data, return data as object
    :param page: selenium webdriver object
    :param own_client: own GUI flag
    :return: data object
    """
    wait_120s = WebDriverWait(page, 120)
    response = {'data': None, 'msg': '', }
    total = page.find_element_by_xpath('//label[@id="uiLblTotalDesierdSum"]').text.replace(',', '')
    try:
        wait_120s.until(present((By.XPATH, MORT_RESULT_ROWS_XPATH)))
    except TimeoutException:
        err_msg = 'No data div present!'
        response.update({'msg': err_msg})
        logger.error(err_msg)
        hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_data')
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_no_data_div': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
    else:
        page.execute_script(f'document.querySelectorAll("{MORT_KILL_LIST}").forEach(function(element) {{element.remove();}})')
        page.execute_script(JS_SCROLL_DOWN)
        page.set_window_size(hb_win_size(page, 'Width'), hb_win_size(page, 'Height'))
        # sleep(WAIT_01)
        if own_client:
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_parsing')
        result_rows = page.find_elements_by_xpath(MORT_RESULT_ROWS_XPATH)

        if result_rows:
            msg = f'{len(result_rows)} data rows found'
            response.update({'data': [], "TotalAmountOfInsurance": total, 'msg': msg})
            logger.debug(msg)
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_{len(result_rows)}_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})

            for idx, row in enumerate(result_rows):
                page_data = {}

                link = row.find_element_by_xpath(MORT_COMPANY_LINK_XPATH_REL)
                page_data['Link'] = link.get_attribute('href')
                page_data['CompanyName'] = link.find_element_by_xpath('./img').get_attribute('alt')
                try:
                    row.find_element_by_xpath(MORT_NO_OFFER_XPATH_REL)
                except NoSuchElementException:
                    first_prem = row.find_element_by_xpath(MORT_1ST_PREM_XPATH_REL).text.replace(',', '')
                    avg_prem = row.find_element_by_xpath(MORT_AVG_PREM_XPATH_REL).text.replace(',', '')
                    tot_prem = row.find_element_by_xpath(MORT_TOT_PREM_XPATH_REL).text.replace(',', '')
                    comment = row.find_element_by_xpath(MORT_COMMENT_XPATH_REL).get_attribute('onclick').split('\'')[1]
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
                data_div = wait_120s.until(present((By.XPATH, MORT_GRPH_INFO_XPATH)))
            except TimeoutException:
                err_msg = 'No chart info present!'
                response.update({'msg': err_msg})
                logger.error(err_msg)
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_no_info')
                if own_client:
                    response.update({f'{page.current_url.split("=")[-1]}_no_info': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            else:
                chart_data = json.loads(data_div.get_attribute(MORT_GRPH_DATA_ATTR))
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


def mortgage_view(request):
    """
    Collect data from Mortgage Insurance page
    :param request: request
    :return: data as JsonResponse
    """
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'mortgage'})
    # take from request
    req_body = request.body.decode()
    logger.debug(f'Received content: {req_body}')
    req_obj = json.loads(req_body)
    insured = req_obj['ListOfInsured']
    tracks = req_obj['ListOfTracks']
    own_client = bool(req_obj.get('own_client'))

    t_start = round(time(), 2)
    page, err = hb_get_page(MORT_INPUT_URL)
    response = {'data': None, 'msg': err, }
    wait_5s = WebDriverWait(page, 5)
    wait_5s.until(clickable((By.XPATH, '//form[@id="uiFormParameters"]')))
    t_load = round(time(), 2)
    logger.info(f'Page loaded in {t_load - t_start} sec')

    if page:
        logger.debug(f'Setting controls...')

        """
        מספר המסלולים
        """
        nt_action = ActionChains(page)
        nt_ctrl = page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlNumTracks_listbox")]')
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_click_NT')
        nt_ctrl.click()
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_click_NT')
        nt_sel = page.find_element_by_xpath(f'//ul[@id="uiDdlNumTracks_listbox"]/li[{len(tracks)}]')
        nt_action.move_to_element(nt_sel)
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_select_NT')
        nt_action.perform()
        nt_sel.click()
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_select_NT')

        """
        מספר המבוטחים
        """
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_filling_NI')
        ni_action = ActionChains(page)
        ni_ctrl = page.find_element_by_xpath('//li[contains(@id,"uiDivNumberOfInsured")]')
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_click_NI')
        ni_ctrl.click()
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_click_NI')
        ni_sel = page.find_element_by_xpath(f'//div[contains(@class,"k-animation-container")][1]//ul/li[{len(insured)}]')
        ni_action.move_to_element(ni_sel)
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_select_NI')
        ni_action.perform()
        ni_sel.click()
        # if own_client:
        #     hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_'after_select_NI')

        for idx, ins in enumerate(insured):
            sleep(WAIT_05)
            logger.debug(f'Insured: {idx + 1}')

            """
            תאריך לידה
            """
            bd_inp = page.find_element_by_xpath(f'//input[contains(@id,"uiTxtAge{idx + 1}")]')
            ins_BD = f'01/01/{insured[idx]["BirthDate"].split("/")[-1]}'
            gender_ndx = int(insured[idx]['Gender'])
            ins_GN = ['Male', 'Female'][gender_ndx]
            smoke_ndx = int(insured[idx]['IsSmoking'])
            ins_IS = ['Yes', 'No'][smoke_ndx]
            logger.debug(f'Insured {idx + 1}, BirthDate: {ins_BD}({insured[idx]["BirthDate"]}), Gender: {ins_GN}({gender_ndx}), IsSmoking: {ins_IS}({smoke_ndx})')
            bd_inp.clear()
            sleep(WAIT_01)
            bd_inp.send_keys(ins_BD)

            # try with exceptions
            gender_btn = page.find_element_by_xpath(f'//label[contains(@for,"uiRd{ins_GN}{idx + 1}")]')
            gender_btn.click()

            # try with exceptions
            smoke_btn = page.find_element_by_xpath(f'//label[contains(@for,"uiRdSmoke{ins_IS}{idx + 1}")]')
            smoke_btn.click()

        for idx, ins in enumerate(tracks):
            sleep(WAIT_05)
            track_DS = str(tracks[idx]['DesiredSum'])
            track_DP = str(tracks[idx]['DesiredPeriod'])
            track_IT = tracks[idx]["InterestType"]
            track_IR = str(tracks[idx]['InterestRate'])
            ind = idx + 1
            logger.debug(f'Track:{ind} ,DS:{track_DS}, DP:{track_DP}, IT:{track_IT}, IR:{track_IR}')

            """
            תקופת ביטוח
            """
            page.find_element_by_xpath(f'//input[contains(@id,"uiLoanDesiredPeriod{idx + 1}")]/preceding-sibling::input').click()
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_send_DP_{ind}')
            # noinspection PyBroadException
            try:
                page.find_element_by_xpath(f'//input[contains(@id,"uiLoanDesiredPeriod{idx + 1}")]').send_keys(track_DP)
                sleep(WAIT_05)
            except:
                err_msg = 'Could not set תקופת ביטוח!'
                logger.error(err_msg)
                response.update({'msg': err_msg})
                if own_client:
                    hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_sent_DP_{ind}')
                return -1, response
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_send_DP_{ind}')

            """
            סכום ביטוח
            """
            page.find_element_by_xpath(f'//input[contains(@id,"uiLoanDesiredSum{idx + 1}")]/preceding-sibling::input').click()
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_send_DS_{ind}')
            # noinspection PyBroadException
            try:
                page.find_element_by_xpath(f'//input[contains(@id,"uiLoanDesiredSum{idx + 1}")]').send_keys(track_DS)
                sleep(WAIT_05)
            except:
                err_msg = 'Could not set סכום ביטוח!'
                logger.error(err_msg)
                response.update({'msg': err_msg})
                if own_client:
                    hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_sent_DS_{ind}')
                return -1, response
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_send_DS_{ind}')

            """
            שיעור הריבית
            """
            page.find_element_by_xpath(f'//input[contains(@id,"uiTxtInterestRate{idx + 1}")]/preceding-sibling::input').click()
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_send_IR_{ind}')
            # noinspection PyBroadException
            try:
                page.find_element_by_xpath(f'//input[contains(@id,"uiTxtInterestRate{idx + 1}")]').send_keys(track_IR)
                sleep(WAIT_05)
            except:
                err_msg = 'Could not set שיעור הריבית!'
                logger.error(err_msg)
                response.update({'msg': err_msg})
                if own_client:
                    hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_sent_IR_{ind}')
                return -1, response
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_send_IR_{ind}')

            """
            סוג הריבית
            """
            it_ctrl = page.find_element_by_xpath(f'//span[contains(@aria-owns,"uiDdlInterestType{ind}_listbox")]')
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_click_IT_{ind}')
            it_ctrl.click()
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_click_IT_{ind}')
            it_sel = page.find_element_by_xpath(f'//div[contains(@class,"k-animation-container")]//ul[@id="uiDdlInterestType{ind}_listbox"]/li[{track_IT}]')
            it_action = ActionChains(page)
            it_action.move_to_element(it_sel)
            it_action.perform()
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_before_select_IT_{ind}')
            it_sel.click()
            if own_client:
                hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_after_select_IT_{ind}')

        # hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_submit')
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_submit': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})

        submit_btn = page.find_element_by_xpath(MORT_SUBMIT_BTN_XPATH)
        submit_btn.click()
        t_submit = round(time(), 2)
        logger.debug(f'Controls set in {t_submit - t_load} sec')
        sleep(WAIT_SEC)
        error_spans = []
        for e_s in page.find_elements_by_xpath('//span[contains(@class,"k-invalid-msg")]'):
            if e_s.text:
                error_spans.append(e_s)
        # errors = ''.join([e.text for e in error_spans])
        if error_spans:
            # logger.error(f'{len(error_spans)} error(s) on page, resetting controls...')
            # errors = ''
            # for e in error_spans:
            #     if e.text:
            #         errors += f', {e.text}'
            err_msg = f'Could not set {len(error_spans)} controls!'
            logger.error(err_msg)
            response.update({'msg': err_msg})
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_not_set')
            if own_client:
                response.update({f'{page.current_url.split("=")[-1]}_not_set': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})

        else:
            logger.debug(f'Controls successfully set.')
            response.update(parse_page_mortgage(page, own_client))
            t_parse = round(time(), 2)
            logger.debug(f'Results t_parse in {t_parse - t_submit} sec')
            logger.info(f'Page t_parse in {round(time(), 2) - t_submit} sec')

    t_total = round(time() - t_start, 2)
    logger.info(f'Backend total: {t_total} sec')
    if own_client:
        response.update({'t_total': t_total})
    return JsonResponse(response)
