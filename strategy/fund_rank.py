import os

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


_rank_url = 'https://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn10000;' \
      'ddesc;qsd20211014;qed20221014;qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
_source_file_path = '/Users/dealmoon/WorkSpace/MINE_GIT_PY/FundCrawler/results/'
_filtered_fund_file_path = 'fund.csv'
_output_file_path = 'fund-rank.csv'
_fund_list = []
_filtered_fund = {}
_get_top_n = 3000
_min_fund_num = 50


def get_filtered_fund():
    with open(_source_file_path + _filtered_fund_file_path) as f:
        for line in f:
            arr = line.replace("\n", "").split(",")
            _filtered_fund[arr[1].replace("'", "")] = arr


def rank_and_filter():
    global _fund_list
    fund_list = _fund_list
    #计算近3年平均涨幅
    total = 0
    size = 0

    for info in fund_list:
        if info[15] != 0:
            total = total + info[15]
            size = size + 1
    avg = round(total / size, 3)
    for info in fund_list:
        if info[15] == 0:
            info[15] = avg

    # 取前3年的前n%
    fund_list = get_top_n(fund_list, 0.9, 15)

    # 取前2年的前n%
    fund_list = get_top_n(fund_list, 0.8, 14)

    # 取前1年的前n%
    fund_list = get_top_n(fund_list, 0.7, 13)

    # 取前半年的前n%
    fund_list = get_top_n(fund_list, 0.6, 12)

    # 取前3月的前n%
    fund_list = get_top_n(fund_list, 0.5, 11)

    # 取前1月的前n%
    fund_list = get_top_n(fund_list, 0.4, 10)

    # 取前1周的前n%
    fund_list = get_top_n(fund_list, 0.3, 9)

    # 根据基金规模倒序
    _fund_list = sorted(fund_list, key=lambda k: float(k[3]), reverse=True)


def get_top_n(fund_list, top_n_percent, key):
    fund_list = sorted(fund_list, key=lambda k: k[key], reverse=True)
    top_n = int(len(fund_list) * top_n_percent)
    if top_n < _min_fund_num: top_n = _min_fund_num
    return fund_list[:top_n]

def save_csv():
    global _fund_list
    new_file_path = _source_file_path + _output_file_path
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    with open(new_file_path, 'a', encoding='utf-8') as f:
        for fund_info in _fund_list:
            line = ''
            index = 0
            for td in fund_info:
                if index >= 5:
                    line = line + str(td) + ","
                else:
                    line = line + td + ","
                index = index + 1
            f.write(line + '\n')
    f.close


def get_fund_rank_data():
    global _fund_list
    co = webdriver.ChromeOptions()
    # 是否有浏览界面，False：有；True：无
    co.headless = True
    chrome_service = Service(r'/Users/dealmoon/WorkSpace/MINE_GIT_PY/FundCrawler/strategy/chromedriver')
    browser = webdriver.Chrome(service=chrome_service, options=co)
    browser.get(_rank_url)
    main_table = browser.find_element(By.ID, 'dbtable')
    tbody = main_table.find_element(By.TAG_NAME, 'tbody')
    funds_elems = tbody.find_elements(By.TAG_NAME, 'tr')

    funds_elems = funds_elems[:_get_top_n]
    row = 1
    for fund in tqdm(funds_elems):
        td_list = fund.find_elements(By.TAG_NAME, 'td')
        index = 0

        fund_info = []
        is_in_pool = True
        for td in td_list:
            if index == 2:
                code = td.text
                fund_info.append(code)
                if code not in _filtered_fund:
                    # print("code:%s is not in filtered fund list" % code)
                    is_in_pool = False
                    break
                f_info = _filtered_fund.get(code)
                fund_info.append(f_info[0])
                fund_info.append(f_info[3])
            if index == 3:
                a_elm = td.find_element(By.TAG_NAME, "a")
                fund_info.append(a_elm.get_attribute("title"))
            elif index == 1 or 4 <= index <= 17:
                v_str = td.text.replace('%', '')
                if index <= 13 and v_str.find("---") > -1:
                    # print("less then 2 years,code:%s", code)
                    is_in_pool = False
                    break
                if index >= 5:
                    v = 0
                    if v_str.find("---") > -1: v_str = '0'
                    try:
                        v = float(v_str)
                    except (ValueError, ArithmeticError):
                        print("cast error, code:%s, v_str:%s" % (code, v_str))
                    fund_info.append(v)
                else:
                    fund_info.append(v_str)
            index = index + 1

        if is_in_pool:
            _fund_list.append(fund_info)
        row = row + 1
    browser.close()


def rank_fund():
    get_filtered_fund()
    # print(len(_filtered_fund))
    get_fund_rank_data()
    rank_and_filter()
    save_csv()


if __name__ == '__main__':
    rank_fund()
