# -*- coding:UTF-8 -*-
"""
基金信息筛选过滤

"""

import os

_source_file_path = '/Users/dealmoon/WorkSpace/MINE_GIT_PY/FundCrawler/results/'
_output_file_path = 'fund.csv'
# _fund_file_name = ["指数型-股票", "混合型-平衡", "债券型-可转债", "QDII", "混合型-偏债", "混合型-灵活", "债券型-混合债",
#                    "债券型-长债", "混合型-偏股", "债券型-中短债", "股票型"]
_fund_file_name = ["指数型-股票", "混合型-平衡", "QDII", "混合型-灵活", "混合型-偏股", "股票型"]
_name_exclude = ["c", "C", "定开", "持有", "封闭"]

# 最小规模
_fund_size_min = 10
total = 0
pool_total = 0
fund_list = []


def filter_fund():
    global total, pool_total, fund_list
    for file_name in _fund_file_name:
        try:
            file_name_full = _source_file_path + file_name + '.csv'
            with open(file_name_full) as f:
                for line in f:
                    if '基金名称' in line:
                        continue
                    arr = line.split(',')
                    if len(arr) < 3:
                        print('length error')
                    fund_size = arr[2]
                    ext_index = fund_size.find('亿元')
                    if ext_index > -1:
                        fund_size = fund_size[0:ext_index]
                        try:
                            if '--' in fund_size:
                                # print("fund size is null, %s", line)
                                continue
                            fund_fize_f = float(fund_size)
                            if fund_fize_f >= _fund_size_min:
                                name = arr[0]

                                is_exclude = False
                                for exclude_name in _name_exclude:
                                    if name.find(exclude_name) > -1:
                                        is_exclude = True
                                        break
                                if is_exclude: continue
                                # print(file_name + "-->" + line + "***" + str(fund_fize_f))
                                pool_total = pool_total + 1
                                fund_list.append([file_name, arr[1], arr[0], fund_fize_f])

                            else:
                                pass
                                # print(line + "XXXXXXXXX" + str(fund_fize_f))

                            total = total + 1
                        except (ValueError, ArithmeticError):
                            pass
                            # print("fund size error, %s" % line)
                    else:
                        print("fund size error, %s" % fund_size)
                    # print(file_name + "," + arr[0] + "," + arr[1] + "," + arr[2])

            f.close()
        except FileNotFoundError:
            print('file name:%s is not exist!!' % file_name_full)

    new_file_path = _source_file_path + _output_file_path
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    # 根据基金规模倒序
    fund_list = sorted(fund_list, key=lambda k: k[3], reverse=True)

    with open(new_file_path, 'a', encoding='utf-8') as f:
        for fund in fund_list:
            line = fund[0] + ",'" + fund[1] + "'," + fund[2] + "," + str(fund[3])
            print(line)
            f.write(line + '\n')
    f.close

    print("total:%d, pool_total:%d" % (total, pool_total))


if __name__ == '__main__':
    filter_fund()
