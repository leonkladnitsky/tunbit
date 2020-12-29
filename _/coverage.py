# HarBit Isurance coverage (General, Life, Health) view and result page parser.

from _.utils import *

logger = getLogger(__name__)

COVERAGE_INPUT_URL = 'https://harb.cma.gov.il'
COVERAGE_FOUND_URL = 'https://harb.cma.gov.il/Overview'
COVERAGE_DATA_URL = 'https://harb.cma.gov.il/Results?id=-1'
COVERAGE_URL_GENERAL = 'Results?id=7'
COVERAGE_URL_HEALTH = 'Results?id=6'
COVERAGE_URL_LIFE = 'Results?id=5'
COVERAGE_CAPTCHA_XPATH = '//img[@id="LocateBeneficiariesCaptcha_CaptchaImage"]'


def parse_page_coverage(page, own_client, ins_type, cnt):
    """
    Parse result page for insurance proposals data, return data as object
    :param page: selenium webdriver object
    :param own_client: own GUI flag
    :param ins_type:
    :param cnt:
    :return: data object
    """

    page.execute_script(JS_SCROLL_DOWN)
    response = {}

    upd_label_xpath = f'//div[contains(@class,"hidden-xs") and contains(@class,"updated")]'
    upd_label = page.find_element_by_xpath(upd_label_xpath).text
    logger.info(f'{ins_type}UpdatedOn: {upd_label}')

    if cnt:
        row_xpath = f'//div[contains(@class,"hidden-xs")]//div[contains(@class,"sub") and contains(@class,"borderUp{ins_type}")]'
        result_rows = page.find_elements_by_xpath(row_xpath)

        if result_rows:
            # result_rows.reverse()
            msg = f'{ins_type}: {len(result_rows)} data rows found'
            response.update({f'{ins_type}Insurances': [], f'{ins_type}UpdatedOn': upd_label})
            # response.update({'data': [], 'msg': msg})
            logger.debug(msg)
            # if own_client:
            #     hb_save_page_screenshot(page, f'{ins_type}_{len(result_rows)}_rows')
            # if own_client:
            #     response.update({f'{ins_type}_{len(result_rows)}_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})

            global_data = []
            for idx, row in enumerate(result_rows):

                pol_num = row.find_element_by_xpath('./div[3]').text
                type_col = row.find_element_by_xpath('./div[1]')
                d_p_n = type_col.get_attribute('data-polnum')
                subrow_xpath = f'//div[contains(@class,"hidden-xs")]//div[contains(@class,"subSunPolicyNum-{d_p_n}")]'
                exp_btn_xpath = f'./div[contains(@class,"bgSecondaryBranchName ") and contains(@class,"innerButExt{ins_type}P")]'
                try:
                    row.find_element_by_xpath(exp_btn_xpath).click()
                except:
                    pass
                    # logger.warning(f'Could not open details for {ins_type}')

                link = row.find_element_by_xpath(f'./div[5]//a[contains(@class,"companyLink")]')

                global_data.append({
                    'CompanyLink': link.get_attribute('href'),
                    'CompanyName': link.find_element_by_xpath('./img').get_attribute('alt'),
                    'Type': type_col.text,
                    'InsurancePeriod': row.find_element_by_xpath('./div[2]').text,
                    'AnnualPremium': row.find_element_by_xpath('./div[3]').text.replace('\n', ' ').strip(),
                    'PolicyNumber': pol_num,
                    'ComprehensiveDetails': [],
                    'Note': ''
                })

                sub_rows = page.find_elements_by_xpath(subrow_xpath)
                if len(sub_rows):
                    logger.info(f'{len(sub_rows)} info items found for police {global_data[idx]["PolicyNumber"]}')
                    for s_row in sub_rows:
                        # logger.debug(f'{s_row.get_attribute("class")}')
                        name = s_row.find_element_by_xpath('./div[1]').text
                        span = s_row.find_element_by_xpath('./div[2]').text
                        prem = s_row.find_element_by_xpath('./div[3]').text.replace('\n', ' ').strip()
                        logger.debug(f'Label: {name}, Period: {span}, Premya: {prem}')
                        global_data[idx]['ComprehensiveDetails'].append({'Label': name, 'Period': span, 'Premya': prem})
                # else:
                #     logger.debug(f'No info items found for police {global_data[idx]["PolicyNumber"]}')
                #     # global_data[idx]['ComprehensiveDetails'] = []
                #     # page_data['CompanyLogo'] = link.find_element_by_xpath('./img').get_attribute('src')
                # del global_data[idx]['InfoItems']

                response[f'{ins_type}Insurances'].append(global_data[idx])

                if not global_data[idx]['PolicyNumber']:
                    logger.error(f'Row WITHOUT PolicyNumber: {global_data[idx]}!!!')
                    if own_client:
                        # global_data[idx]['row'] = f'data:image/jpeg;base64,{row.screenshot_as_base64}'
                        response.update({f'{ins_type}_no_policy_num': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            if own_client:
                response.update({f'{ins_type}_result': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
                hb_save_page_screenshot(page, f'{ins_type}_result')
        else:
            err_msg = 'No result rows found!'
            response.update({'msg': err_msg})
            logger.error(err_msg)
            hb_save_page_screenshot(page, f'{ins_type}_no_rows')
            if own_client:
                response.update({f'{ins_type}_no_rows': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})

    return response


def coverage_view(request):
    """
    Collect data from Coverages page
    :param request: request
    :return: data as JsonResponse
    """
    t_start = round(time(), 2)

    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'coverage'})

    # take from request
    req_body = request.body.decode()
    logger.info(f'Received content: {req_body}')
    req_obj = json.loads(req_body)
    id_number = req_obj.get('IdNumber', '0')
    issue_date = req_obj.get('IssueDate')
    [issue_day, issue_month, issue_year] = [int(_) for _ in issue_date.split('/')]
    own_client = bool(req_obj.get('own_client'))
    left_in3yrs = int(req_obj.get('LeftCountryInThreeYears'))
    psprt_issd = int(req_obj.get('PassportIssuedInThreeYears'))
    page, err = hb_get_page(COVERAGE_INPUT_URL)
    response = {'data': None, 'msg': err, }
    t_load = round(time(), 2)
    logger.info(f'Page {page.current_url} loaded in {t_load - t_start} sec')

    if page:
        response = {'msg': err, 'data': {}}
        wait_120s = WebDriverWait(page, 120)
        wait_120s.until(clickable((By.XPATH, '//button[@id="butFindMine"]')))
        page.find_element_by_xpath('//button[@id="butFindMine"]').click()

        """
        זהות
        """
        idnumber_input = page.find_element_by_xpath('//input[@id="txtId"]')
        if idnumber_input:
            idnumber_input.clear()
            sleep(WAIT_01)
            idnumber_input.send_keys(id_number)

        """
        דרכון
        """
        psprt_buttons = page.find_elements_by_xpath('//input[@name="PassportSwitch"]/following-sibling::label')
        psprt_buttons[psprt_issd].click()
        # logger.debug(f'Psprt is set")

        """
        חו"ל
        """
        left_buttons = page.find_elements_by_xpath('//input[@name="CuntryOutSwitch"]/following-sibling::label')
        left_buttons[left_in3yrs].click()
        # logger.debug(f'Left is set")

        """
        לתנאי השימוש
        """
        ok_input = page.find_element_by_xpath('//input[@id="cbAproveTerm"]')
        ok_input.click()
        # logger.debug(f'Term is set")

        wait_5s = WebDriverWait(driver=page, timeout=5, poll_frequency=0.1)
        wait_5s.until(all_visible((By.XPATH, COVERAGE_CAPTCHA_XPATH)))
        cap_img = page.find_element_by_xpath(COVERAGE_CAPTCHA_XPATH)
        cap_img_b64 = cap_img.screenshot_as_base64

        data = {'image': f'data:image/jpeg;base64,{cap_img_b64}', 'is_case': True, 'is_phrase': False, 'is_math': False}
        if own_client:
            response.update({f'{page.current_url.split("=")[-1]}_captcha': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
            hb_save_page_screenshot(page, f'{page.current_url.split("=")[-1]}_captcha')

        cap_thr = hb_solve_captcha_bsc(data)
        t_cap_sent = round(time(), 2)
        logger.debug(f'Captcha is sent to BSC...')

        """
        הנפקה
        """
        action = ActionChains(page)
        page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlDay_listbox")]').click()
        day = page.find_element_by_xpath(f'//ul[@id="uiDdlDay_listbox"]/li[contains(@data-offset-index,"{issue_day}")]')
        action.move_to_element(day)
        action.perform()
        day.click()
        # logger.debug(f'Day is set")

        action = ActionChains(page)
        page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlMonth_listbox")]').click()
        month = page.find_element_by_xpath(f'//ul[@id="uiDdlMonth_listbox"]/li[contains(@data-offset-index,"{issue_month}")]')
        action.move_to_element(month)
        action.perform()
        month.click()
        # logger.debug(f'Month is set")

        action = ActionChains(page)
        page.find_element_by_xpath('//span[contains(@aria-owns,"uiDdlYear_listbox")]').click()
        year = page.find_element_by_xpath(f'//ul[@id="uiDdlYear_listbox"]/li[contains(@data-offset-index,"{datetime.now().year + 1 - issue_year}")]')
        action.move_to_element(year)
        action.perform()
        year.click()
        # logger.debug(f'Year is set")

        logger.info(f'Controls set in {round(time() - t_load, 2)} sec, waiting for captcha ...')
        """
        צפיה
        """
        # noinspection PyBroadException
        try:
            res = cap_thr.result()
        except Exception as e:
            t_cap_got = round(time() - t_cap_sent, 2)
            err_msg = f'BCS timeout: {t_cap_got} sec'
            logger.error(err_msg)
            res = {'id': None, 'text': None, 'status': err_msg}
            response.update({'msg': err_msg})
        else:
            t_cap_got = round(time() - t_cap_sent, 2)
            logger.info(f'BCS replied [{res}] in {t_cap_got} sec')
            if own_client:
                response.update({'t_captcha': t_cap_got})

        if res and ('status' in res) and (res['status'] == 'completed') and ('text' in res) and res['text']:
            """
            אבטחה
            """
            code = res['text']
            captcha_input = page.find_element_by_xpath('//input[@id="CaptchaCode"]')
            captcha_input.clear()
            captcha_input.send_keys(code)
            t_submit = round(time(), 2)

            page.find_element_by_xpath('//button[@id="butIdent"]').click()
            sleep(WAIT_05)

            try:
                wait_120s.until(url_to_be(COVERAGE_FOUND_URL))
            except TimeoutException as e:
                err_msg = f'Page change timeout: {e}, {COVERAGE_FOUND_URL}'
                logger.error(err_msg)
                response.update({'msg': err_msg})
                hb_save_failed_captcha(cap_img, code)
            else:
                sleep(WAIT_05)
                t_change = round(time(), 2)
                logger.info(f'Page changed in {t_change - t_submit} sec')
                page.execute_script("$('.modal').modal('hide')")
                sleep(WAIT_05)
                link_xpath = '//div[contains(@class,"navigateIcon")]'
                link_elems = page.find_elements_by_xpath(link_xpath)
                cnt_elems = page.find_elements_by_xpath(link_xpath + '/div[contains(@class,"counter")]')
                ins_types = ['General' if 'global' in c.get_attribute('class') else c.get_attribute('class')[8:-7].title() for c in cnt_elems]

                counters = [int(c) if c.isdigit() else 0 for c in [c.text for c in cnt_elems]]
                urls = [l.get_attribute('onclick').split('\'')[-2] for l in link_elems]
                if not (len(ins_types) == len(counters) == len(urls)):
                    logger.warning(f'Data mismatch: {len(ins_types)} ? {len(counters)} ? {len(urls)} ')

                logger.debug(f'Insurances: {[_ for _ in zip(ins_types, counters, urls)]}')

                for (i_t, cnt, url) in list(zip(ins_types, counters, urls)):
                    t_page = time()
                    page.get(COVERAGE_INPUT_URL + url)
                    try:
                        wait_120s.until(url_to_be(COVERAGE_INPUT_URL + url))
                    except TimeoutException:
                        err_msg = f'No url match for {COVERAGE_INPUT_URL + url}'
                        logger.error(err_msg)
                        response.update({'msg': err_msg, 'url': page.current_url})
                        hb_save_page_screenshot(page, f'{i_t}_wrong_url')
                        if own_client:
                            response.update({f'{i_t}_wrong_url': f'data:image/jpeg;base64,{hb_get_page_screenshot(page)}'})
                    else:
                        t_load = round(time() - t_page, 2)
                        logger.info(f'Page {i_t} loaded in {t_load} sec')
                        response['data'].update(parse_page_coverage(page, own_client, i_t, cnt))
                        # t_parse = round(time() - t_load, 2)
                        # logger.info(f'Page {i_t} parsed in {t_parse} sec')
                        # response.update({f't_parse_{i_t} ': t_parse})

        else:
            hb_save_failed_captcha(cap_img)
            err_msg = f'Captcha NOT completed: {res}'
            logger.error(err_msg)
            response.update({'msg': err_msg})
            if own_client:
                response.update({'base64': f'data:image/jpeg;base64,{cap_img_b64}'})

    t_total = round(time() - t_start, 2)
    logger.info(f'Backend done in {t_total} sec')
    if own_client:
        response.update({'t_total': t_total})
    page.quit()
    return JsonResponse(response)
