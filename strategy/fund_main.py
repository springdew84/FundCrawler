# -*- coding:UTF-8 -*-
import time

import fund_rank
import fund_filter


def rank():
    print('start filter fund list...........')
    fund_filter.filter_fund()
    time.sleep(10)
    print('start rank fund list...........')
    fund_rank.rank_fund()
    print('all success!!')


if __name__ == '__main__':
    rank()
