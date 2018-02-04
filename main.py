import os
import re
import time
import sys
import Utils

url = "http://otcbtc.com"

trade_suffix = "{trade_type}_offers?currency={curr_type}&fiat_currency=cny&payment_type=all"
currency_types = ["BTC", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "IOST", "KIN", "NAS",
                  "SWFTC", "TNB", "USDT"]

#currency_types = ["ETH", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "KIN", "TNB", "USDT"]

#currency_types = ["ETH", "OTB"]
#currency_types = ["EOS"]
base_type = "ETH"


def main():
    while True:
        for currency in currency_types:
            parse_both(currency, base_type)

def parse_both(ctype, btype):
    cnt = get_money_trade_response("sell", ctype)
    buy_lowest_price = get_buy_lowest_price(cnt)
    time.sleep(2)
    cnt = get_money_trade_response("buy", ctype)
    sell_highest_price = get_sell_highest_price(cnt)
    time.sleep(2)
    cnt = get_money_trade_response("sell", btype)
    base_buy_lowest_price = get_buy_lowest_price(cnt)
    time.sleep(2)
    cnt = get_money_trade_response("buy", btype)
    base_sell_highest_price = get_sell_highest_price(cnt)
    time.sleep(2)
    cnt = get_coin_to_coin_response(ctype, btype)
    red_buy_lowest_price = get_coin_to_coin_price(cnt, "buy")
    green_sell_highest_price = get_coin_to_coin_price(cnt, "sell")
    print("[{ctype}] L: {clp} - H: {chp} | [{btype}] L: {blp} - H: {bhp}".format(
        ctype=ctype, clp=buy_lowest_price, chp=sell_highest_price,
        btype=btype, blp=base_buy_lowest_price, bhp=base_sell_highest_price)
    )
    try:
        sell_rate = sell_highest_price / base_buy_lowest_price
        buy_rate = buy_lowest_price / base_sell_highest_price
        sell_msg = "sell rate: {rate1} | c2c sell rate: {rate2}".format(rate1=sell_rate, rate2=red_buy_lowest_price)
        buy_msg = "buy rate: {rate1} | c2c buy rate: {rate2}".format(rate1=buy_rate, rate2=green_sell_highest_price)
        if sell_rate > red_buy_lowest_price:
            print("You should buy {good1}({price1})  and sell {good2}({price2}) ==> {msg}".format(
                good1=btype, price1=base_buy_lowest_price, good2=ctype, price2=sell_highest_price, msg=sell_msg))
            print("Example: buy {good1} with 10000 at {price1} multi {rate1} and sell {good} at {price2} == {total}, "
                  "get {money}".format(good1=btype, price1=base_buy_lowest_price, rate1=red_buy_lowest_price, good=ctype,
                                       price2=sell_highest_price,
                                       total=(10000/base_buy_lowest_price/red_buy_lowest_price*sell_highest_price),
                                       money=(10000/base_buy_lowest_price/red_buy_lowest_price*sell_highest_price) - 10000
            ))
        if buy_rate < green_sell_highest_price:
            print("You should buy {good1}({price1}) and sell {good2}({price2}) ==> {msg}".format(
                good1=ctype, price1=buy_lowest_price, good2=btype, price2=base_sell_highest_price, msg=buy_msg))
            print("Example: buy {good} with 10000 at {price1} multi {rate1} and sell {good1} at {price2} == {total}, "
                  "get {money}".format(price1=buy_lowest_price, rate1=green_sell_highest_price, good=ctype, good1=btype,
                                       price2=base_sell_highest_price,
                                       total=(10000/buy_lowest_price*green_sell_highest_price*base_sell_highest_price),
                                       money=(10000/buy_lowest_price*green_sell_highest_price*base_sell_highest_price)-10000
            ))
    except Exception, e:
        print e

def parse(ctype):
    time.sleep(10)
    cnt = get_money_trade_response("sell", ctype)
    buy_lowest_price = get_buy_lowest_price(cnt)
    buy_lowest_owner = get_buy_lowest_owner(cnt)
    buy_total_page_count = get_total_page(cnt)
    time.sleep(2)
    cnt = get_money_trade_response("buy", ctype)
    sell_highest_price = get_sell_highest_price(cnt)
    sell_highest_owner = get_sell_highest_owner(cnt)
    sell_total_page_count = get_total_page(cnt)
    rate = (buy_lowest_price - sell_highest_price) / buy_lowest_price
    print "[{ctype}] - Lowest buy price: {l_p} [by: {l_owner}] ({buy_page}) - " \
          "Highest_sell_price: {h_p}  [by: {h_owner}] ({sell_page}) | rate: {rate}".\
        format(ctype = ctype, l_p = buy_lowest_price, h_p = sell_highest_price, rate = rate,
               buy_page = buy_total_page_count, sell_page = sell_total_page_count,
               l_owner = buy_lowest_owner, h_owner = sell_highest_owner)

def do_request(url):
    rsp, cnt = Utils.Web.do_get(url)
    return cnt


def get_money_trade_response(tade_type="buy", curr_type="EOS"):
    real_url = os.path.join(url, trade_suffix).format(trade_type=tade_type, curr_type=curr_type)
    return do_request(real_url)

def get_coin_to_coin_response(curr_type, base_type):
    coin_suffix = curr_type.lower() + base_type.lower()
    real_url = os.path.join("https://bb.otcbtc.com/exchange/markets/", coin_suffix)
    return do_request(real_url)

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

def get_coin_to_coin_price(rsp, trade_type):
    found = False
    rsp_list = rsp.splitlines()
    for index, value in enumerate(rsp_list):
        if "gon.orderbook" in value:
            found = True
            break
    key_word = "asks" if trade_type == "buy" else "bids"
    return float(re.search("%s\":\[\[\"(\d+\.\d+)" % key_word, rsp_list[index]).groups()[0]) if found else 0.0



if __name__ == "__main__":
    argv = sys.argv
    if len(argv) <= 1:
        pass
    else:
        currency_types = [argv[1]]
    main()
