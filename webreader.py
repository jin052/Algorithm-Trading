import requests
import re
from bs4 import BeautifulSoup
import datetime


def get_financial_statements(code):
    re_enc = re.compile("encparam: '(.*)'", re.IGNORECASE)
    re_id = re.compile("id: '([a-zA-Z0-9]*)' ?", re.IGNORECASE)

    url = "http://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd={}".format(code)
    html = requests.get(url).text
    encparam = re_enc.search(html).group(1)
    encid = re_id.search(html).group(1)


    url = "http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd={}&fin_typ=0&freq_typ=A&encparam={}&id={}".format(code, encparam, encid)
    headers = {"Referer": "HACK"}
    html = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html, "html5lib")
    dividend = soup.select("table:nth-of-type(2) tr:nth-of-type(31) td span")
    years = soup.select("table:nth-of-type(2) th")

    dividend_dict = {}

    for i in range(len(dividend)):
        dividend_dict[years[i+3].text.strip()[:4]] = dividend[i].text

    return dividend_dict

def get_estimated_dividend_yield(code):
    dividend_yield = get_financial_statements(code)
    if len(dividend_yield) == 0 :
        return'0'

    dividend_yield = sorted(dividend_yield.items())[-1]
    return dividend_yield[1]

def get_3year_treasury():
    url = "http://www.index.go.kr/potal/main/EachDtlPageDetail.do?idx_cd=1073"
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html5lib')
    treasury_list = soup.find('tr', {'data-id' : 'tr_107301_1'})
    td_data = treasury_list.select('td')

    treasury_3year = {}
    start_year = 2012

    for i in range(8):
        treasury_3year[start_year] = td_data[i].text
        start_year += 1
    return treasury_3year

def get_current_3year_treasury():
    url = "https://finance.naver.com/marketindex/interestDetail.nhn?marketindexCd=IRR_GOVT03Y"
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'html5lib')
    export = soup.find('div', {'id': 'content'})
    td_data = export.select("em span")
    current_3year_treasury = td_data[0].text + td_data[1].text + td_data[2].text+ td_data[3].text
    return current_3year_treasury


def get_dividend_yield(code):
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd=" + code
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'html5lib')
    dt_data = soup.select("td dl dt")
    dividend_yield = dt_data[-2].text
    dividend_yield = dividend_yield.split(' ')[1]

    if type(dividend_yield) != float:
        dividend_yield = 0
        return dividend_yield

    dividend_yield = dividend_yield[:-1]

    return dividend_yield

def get_previous_dividend_yield(code):
    dividend_yield = get_financial_statements(code)

    now = datetime.datetime.now()
    cur_year = now.year
    previous_dividend_yield = {}

    for year in range(cur_year-4, cur_year):
        if str(year) in dividend_yield.keys():
            previous_dividend_yield[year] = dividend_yield[str(year)]
    return previous_dividend_yield


if __name__ == "__main__":
    dividend_yield = get_dividend_yield('000180')
    print(get_previous_dividend_yield('000180'))
    treasury = get_current_3year_treasury()
    dividend_dict = get_financial_statements("000180")
    print(dividend_dict)
    #print(get_estimated_dividend_yield('000180'))
    pre_dividend_yield = get_previous_dividend_yield('000180')
    #print(pre_dividend_yield)