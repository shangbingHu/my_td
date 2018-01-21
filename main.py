import os
import re
import time
import Utils

url = "http://otcbtc.com"

trade_suffix = "{trade_type}_offers?currency={curr_type}&fiat_currency=cny&payment_type=all"
currency_types = ["BTC", "ETH", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "IOST", "KIN", "NAS",
                  "SWFTC", "TNB", "USDT"]

#currency_types = ["ETH", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "KIN", "TNB", "USDT"]

currency_types = ["ETH", "OTB"]
#currency_types = ["EOS"]


def main():
    while True:
        for currency in currency_types:
            parse(currency)


def parse(ctype):
    time.sleep(10)
    cnt = get_response("sell", ctype)
    buy_lowest_price = get_buy_lowest_price(cnt)
    buy_lowest_owner = get_buy_lowest_owner(cnt)
    buy_total_page_count = get_total_page(cnt)
    time.sleep(2)
    cnt = get_response("buy", ctype)
    sell_highest_price = get_sell_highest_price(cnt)
    sell_highest_owner = get_sell_highest_owner(cnt)
    sell_total_page_count = get_total_page(cnt)
    rate = (buy_lowest_price - sell_highest_price) / buy_lowest_price
    print "[{ctype}] - Lowest buy price: {l_p} [by: {l_owner}] ({buy_page}) - " \
          "Highest_sell_price: {h_p}  [by: {h_owner}] ({sell_page}) | rate: {rate}".\
        format(ctype = ctype, l_p = buy_lowest_price, h_p = sell_highest_price, rate = rate,
               buy_page = buy_total_page_count, sell_page = sell_total_page_count,
               l_owner = buy_lowest_owner, h_owner = sell_highest_owner)

def get_response(tade_type="buy", curr_type="EOS"):
    real_url = os.path.join(url, trade_suffix).format(trade_type=tade_type, curr_type=curr_type)
    #print real_url
    #exit(0)
    rsp, cnt = Utils.Web.do_get(real_url)
    #print cnt
    return cnt


def get_buy_lowest_price(rsp):
    found = False
    rsp_list = rsp.splitlines()
    for index, value in enumerate(rsp_list):
        if "recommend-card__price" in value:
            found = True
            break
    return float(rsp_list[index + 1].strip().replace(",", "")) if found else 0.0

#recommend-card__header--danger
def get_buy_lowest_owner(rsp):
    found = False
    rsp_list = rsp.splitlines()
    for index, value in enumerate(rsp_list):
        if "recommend-card__header--danger" in value:
            found = True
            break
    return re.search(">(.*)<", rsp_list[index + 3].strip()).groups()[0] if found else "NO_BODY"


def get_sell_highest_price(rsp):
    return get_buy_lowest_price(rsp)

def get_sell_highest_owner(rsp):
    return get_buy_lowest_owner(rsp)


def get_total_page(rsp):
    found = False
    rsp_list = rsp.splitlines()
    for index, value in enumerate(rsp_list):
        if "next next_page" in value:
            found = True
            break
    #print
    #return re.match("\d+</a></li> <li class=\"next next_page", value).groups()
    #print value
    return re.search("(\d+)</a></li> <li class=\"next next_page", value).groups()[0] if found else 1


if __name__ == "__main__":
    main()