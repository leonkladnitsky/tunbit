import time
import json
import sys

from django.http import JsonResponse
from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CONTENT_OFFER_URL = 'https://dira.cma.gov.il/Home/FillParameters?InsuranceType=Content'
BUILDING_OFFER_URL = 'https://dira.cma.gov.il/Home/FillParameters?InsuranceType=Structure'
FULLPROP_OFFER_URL = 'https://dira.cma.gov.il/Home/FillParameters?InsuranceType=StructureAndContent'


def get_page(url):
    opts = Options()
    opts.headless = True
    executable_path = './chromedriver' if 'linux' in sys.platform else 'chromdriver.exe'
    browser = webdriver.Chrome(
        executable_path=executable_path,
        options=opts,
        service_args=['--verbose', '--log-path=.\\chromedriver.log']
    )
    browser.get(url)
    time.sleep(1)
    return browser


def submit_page(page, sel_vals, num_vals):
    selects, indexes = find_selections(page)
    assert len(selects) == len(sel_vals)

    triggers, num_inputs = find_numeric(page)
    assert len(triggers) == len(num_vals)

    for i in range(len(sel_vals)):
        selects[i].click()
        time.sleep(0.5)
        print(indexes[i][sel_vals[i]].text)
        indexes[i][sel_vals[i]].click()
        time.sleep(0.1)

    for i in range(len(num_vals)):
        triggers[i].click()
        time.sleep(0.5)
        num_inputs[i].send_keys(str(num_vals[i]))
        print(num_inputs[i].get_attribute('value'))
        time.sleep(0.1)

    submit_btn = page.find_element_by_xpath('//button[@id="uiBtnCalculate"]')
    time.sleep(0.5)
    submit_btn.click()
    time.sleep(5)


def parse_page(page, more_info):
    result_rows = page.find_elements_by_xpath(
        '//div[@id="uiGridResults"]/div/table/tbody/tr[contains(@class,"k-master-row")]')
    response = {'data': [], 'msg': '', }
    for row in result_rows:
        main_cell = row.find_element_by_xpath('./td/table/tbody/tr/td[2]')
        link = main_cell.find_element_by_xpath(
            './div/span[contains(concat(" ",normalize-space(@class)," "),"corp-logo")]/a')
        title = main_cell.find_element_by_xpath('./div/label')
        rating = main_cell.find_element_by_xpath('./div/span/a[contains(@class,"numTxtcolor")]')
        price = main_cell.find_element_by_xpath('./div/span[contains(@class,"resultsTxtcolor")]')
        page_data = {
            'title': title.text,
            'company_name': link.get_attribute('title').split(' , ')[0],
            'company_url': link.get_attribute('href'),
            'service_rating': rating.text,
            'ins_price': price.text,
            'info': []
        }

        if more_info:
            more_info = main_cell.find_element_by_xpath('./div/a[@id="uiamoreinfo"]')
            more_info.click()
            time.sleep(0.1)
            info_items = row.find_elements_by_xpath(
                './following-sibling::tr[contains(@class,"k-detail-row")]/td/div/div[@id="uiDivCompanyRemarks"]/div[contains(@class,"border-company-remarks")]')
            for item in info_items:
                color = item.find_element_by_xpath('./div')
                header = item.find_element_by_xpath('./div/center/b')
                text = item.find_element_by_xpath('./center/p')
                page_data['info'].append({
                    'header': header.text,
                    'text': text.text,
                    'color': color.get_attribute('class').strip().split('-')[1]
                })

        response['data'].append(page_data)
    page.quit()
    return response


def find_selections(page):
    selects = page.find_elements_by_xpath(
        '//span[contains(concat(" ",normalize-space(@class)," "),"k-dropdown-wrap k-state-default")]')
    indexes = [
        page.find_elements_by_xpath(
            '//ul[@id="' + s.find_element_by_xpath("./..").get_attribute('aria-owns') + '"]/li')
        for s in selects
    ]
    assert len(selects) == len(indexes)
    return selects, indexes


def find_numeric(page):
    triggers = page.find_elements_by_xpath(
        '//div/div[contains(@class,"col-sm-6")]/div/span[contains(@class,"k-numerictextbox")]//span[contains(@class,"k-numeric-wrap")]')

    num_inputs = [
        t.find_element_by_xpath(
            './input[@id="' + t.find_element_by_xpath("./../../../../label").get_attribute('for') + '"]')
        for t in triggers

    ]
    return triggers, num_inputs


def content_view(request):
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'content'})

    # take from request
    req = json.loads(request.body)
    c_type_floor = req['c_type_floor']
    c_ins_sum = req['c_ins_sum']
    c_prev_claims = req['c_prev_claims']
    c_more_info = bool(req['c_more_info'])

    sel_vals = [c_type_floor, c_prev_claims]
    num_vals = [c_ins_sum]
    page = get_page(CONTENT_OFFER_URL)
    submit_page(page, sel_vals, num_vals)
    response = parse_page(page, c_more_info)

    return JsonResponse(response)


def building_view(request):
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'building'})

    # take from request
    req = json.loads(request.body)
    b_type_floor = req['b_type_floor']
    b_age = req['b_age']
    b_water_coverage = req['b_water_coverage']
    b_ins_sum = req['b_ins_sum']
    b_prev_claims = req['b_prev_claims']
    b_mortgage = req['b_mortgage']
    b_more_info = bool(req['b_more_info'])

    sel_vals = [b_type_floor, b_water_coverage, b_prev_claims, b_mortgage]
    num_vals = [b_age, b_ins_sum]
    page = get_page(BUILDING_OFFER_URL)
    submit_page(page, sel_vals, num_vals)
    response = parse_page(page, b_more_info)

    return JsonResponse(response)


def fullprop_view(request):
    if request.method == 'GET':
        return render(request, 'index.html', {'page': 'fullprop'})

    # take from request
    req = json.loads(request.body)
    f_type_floor = req['f_type_floor']
    fb_age = req['fb_age']
    f_water_coverage = req['f_water_coverage']
    f_mortgage = req['f_mortgage']
    fb_ins_sum = req['fb_ins_sum']
    fb_prev_claims = req['fb_prev_claims']
    fc_ins_sum = req['fc_ins_sum']
    fc_prev_claims = req['fc_prev_claims']
    f_more_info = bool(req['f_more_info'])

    sel_vals = [f_type_floor, f_water_coverage, f_mortgage, fb_prev_claims, fc_prev_claims]
    num_vals = [fb_age, fb_ins_sum, fc_ins_sum]
    page = get_page(FULLPROP_OFFER_URL)
    submit_page(page, sel_vals, num_vals)
    response = parse_page(page, f_more_info)

    return JsonResponse(response)


def home(request):
    page = request.GET.get('page') or 'content'
    return render(request, 'index.html', {'page': page})
