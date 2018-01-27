import os
import re
import time
import sys
import Utils
from lxml import etree
from copy import deepcopy

url = "http://otcbtc.com"

trade_suffix = "{trade_type}_offers?currency={curr_type}&fiat_currency=cny&payment_type=all"
currency_types = ["BTC", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "IOST", "KIN", "NAS",
                  "SWFTC", "TNB", "USDT"]

#currency_types = ["ETH", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "KIN", "TNB", "USDT"]

#currency_types = ["ETH", "OTB"]
#currency_types = ["EOS"]
BASE_TYPE = "ETH"
SLEEP_SEC = 2
SELL = "buy"
BUY = "sell"
# no matther buy or sell, for me, it's the action not the pulishing


def main():
    while True:
        for currency in currency_types:
            parse_both(currency, BASE_TYPE)

def parse_both(ctype, btype):
    cnt = get_money_trade_response(BUY, ctype)
    buy_lowest_price = get_buy_lowest_price(cnt)
    time.sleep(2)
    cnt = get_money_trade_response(SELL, ctype)
    sell_highest_price = get_sell_highest_price(cnt)
    time.sleep(2)
    cnt = get_money_trade_response(BUY, btype)
    base_buy_lowest_price = get_buy_lowest_price(cnt)
    time.sleep(2)
    cnt = get_money_trade_response(SELL, btype)
    base_sell_highest_price = get_sell_highest_price(cnt)
    time.sleep(2)
    cnt = get_coin_to_coin_response(ctype)
    red_buy_lowest_price = get_coin_to_coin_price(cnt, SELL)
    green_sell_highest_price = get_coin_to_coin_price(cnt, BUY)
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
    cnt = get_money_trade_response(BUY, ctype)
    buy_lowest_price = get_buy_lowest_price(cnt)
    buy_lowest_owner = get_buy_lowest_owner(cnt)
    buy_total_page_count = get_total_page(cnt)
    time.sleep(2)
    cnt = get_money_trade_response(SELL, ctype)
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
    #time.sleep(SLEEP_SEC)
    return cnt


def get_money_trade_response(tade_type=SELL, curr_type="EOS"):
    real_url = os.path.join(url, trade_suffix).format(trade_type=tade_type, curr_type=curr_type)
    return do_request(real_url)

def get_coin_to_coin_response(curr_type):
    coin_suffix = curr_type.lower() + "eth"
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
    key_word = "asks" if trade_type == SELL else "bids"
    return float(re.search("%s\":\[\[\"(\d+\.\d+)" % key_word, rsp_list[index]).groups()[0]) if found else 0.0


def parse_money_to_coin_page(ctn):
    result = []
    try:
        tree = etree.HTML(ctn)
        nodes = tree.xpath("//li[@class='price']/text()")
        prices = [float(str(price).strip().replace(",", "")) for price in nodes if str(price).strip()]
        nodes = tree.xpath("//li[@class='minimum-amount']/text()")
        counts = [float(str(count).strip().replace(",", "").splitlines()[2].strip()) for count in nodes if str(count).strip()]
        price_with_count_list = zip(prices, counts)
        result = price_with_count_list
    except Exception, e:
        print e
    return result


#[[asks_info], [bids_info]]
def parse_coin_to_coin_page(ctn):
    result = [[], []]
    def parse_price_and_count(pcinfo):
        info = [float(item.strip("[").strip("]").strip('"')) for item in pcinfo.split(",")]
        price = [value for (index, value) in enumerate(info) if index % 2 == 0]
        count = [value for (index, value) in enumerate(info) if index % 2]
        return zip(price, count)
    try:
        content = ctn
        start = content.index("gon.orderbook")
        end = content.index("gon.trades")
        content = content[start + 15:end - 2]

        start = content.index("asks")
        end = content.index("bids")

        asks = content[start + 7:end - 3]
        bids = content[end + 7:-1]
        asks_price_with_count_list = parse_price_and_count(asks)
        bids_price_with_count_list = parse_price_and_count(bids)
        result = asks_price_with_count_list, bids_price_with_count_list
    except Exception, e:
        print e
    return result


class Strategy(object):
    def __init__(self, btype, ctype):
        self.btype = btype
        self.ctype = ctype
        self.btype_money_to_coin_buy_info = self.get_money_to_coin_trade_info(BUY, self.btype)
        self.btype_money_to_coin_sell_info = self.get_money_to_coin_trade_info(SELL, self.btype)
        self.ctype_money_to_coin_buy_info = self.get_money_to_coin_trade_info(BUY, self.ctype)
        self.ctype_money_to_coin_sell_info = self.get_money_to_coin_trade_info(SELL, self.ctype)
        self.coin_to_coin_info = self.get_coin_to_coin_info(self.ctype)

    # for sell, the format is: [(price1, count1), (price2, count2)]
    # for buy, the format is: [(price1, total_price1), (price2, total_price2)]
    def get_money_to_coin_trade_info(self, trade_type, curr_type):
        content = get_money_trade_response(trade_type, curr_type)
        return parse_money_to_coin_page(content)

    # [[(sell_price1, sell_count1), (sell_price2, sell_count2)], [(buy_price1, buy_count1), (buy_price2, buy_count2)]]
    def get_coin_to_coin_info(self, curr_type):
        content = get_coin_to_coin_response(curr_type)
        return parse_coin_to_coin_page(content)

    # clean some unused price & count info
    def clean_data_method(self, trade_type, trade_info):
        return trade_info

    def do_clean(self):
        self.btype_money_to_coin_buy_info = self.clean_data_method(BUY, self.btype_money_to_coin_buy_info)
        self.btype_money_to_coin_sell_info = self.clean_data_method(SELL, self.btype_money_to_coin_sell_info)
        self.ctype_money_to_coin_buy_info = self.clean_data_method(BUY, self.ctype_money_to_coin_buy_info)
        self.ctype_money_to_coin_sell_info = self.clean_data_method(SELL, self.ctype_money_to_coin_sell_info)
        self.coin_to_coin_info = self.clean_data_method(SELL, self.coin_to_coin_info)

    def papar_trade(self):
        pass

    def send_order(self):
        pass


class RateStrategy(Strategy):
    def __init__(self, btype, ctype):
        super(RateStrategy, self).__init__(btype, ctype)

    def clean_data_method(self, trade_type, trade_info):
        super(RateStrategy, self).clean_data_method(trade_type, trade_info)
        new_trade_info = deepcopy(trade_info)
        counter = 0
        if len(trade_info) == 1:
            if trade_type == SELL:
                for index, info in enumerate(trade_info):
                    if info[0] * info[1] < 2000.0:
                        del new_trade_info[index - counter]
                        counter += 1
            else:
                for index, info in enumerate(trade_info):
                    if info[1] < 2000.0:
                        del new_trade_info[index - counter]
                        counter += 1

            return new_trade_info
        elif len(trade_info) == 2:
            new_buy_info = deepcopy(new_trade_info[0])
            for index, info in enumerate(new_trade_info[0]):
                if info[0] * info[1] * 6000 < 300:
                    del new_buy_info[index - counter]
                    counter += 1
            new_sell_info = deepcopy(new_trade_info[1])
            for index, info in enumerate(new_trade_info[1]):
                if info[0] * info[1] * 6000 < 300:
                    del new_sell_info[index - counter]
                    counter += 1
            new_trade_info = [new_buy_info, new_sell_info]
        return new_trade_info


    def papar_trade(self):
        super(RateStrategy, self).papar_trade()
        self.do_clean()
        red_lowest_rate = self.coin_to_coin_info[0][0][0]
        green_highest_rate = self.coin_to_coin_info[1][0][0]
        base_buy_lowest_price = self.btype_money_to_coin_buy_info[0][0]
        base_sell_hightest_price = self.btype_money_to_coin_sell_info[0][0]
        curr_buy_lowest_price = self.ctype_money_to_coin_buy_info[0][0]
        curr_sell_highest_price = self.ctype_money_to_coin_sell_info[0][0]

        logic_red_lowest_rate = curr_sell_highest_price / base_buy_lowest_price
        logic_green_highest_rate = curr_buy_lowest_price / base_sell_hightest_price
        print("base_buy_lowest_price: %s | curr_sell_highest_price: %s | red_lowest_rate at the right time: %s" % (
            base_buy_lowest_price, curr_sell_highest_price, red_lowest_rate
        ))
        print("If you want get trade to be done, you should set the red rate lower than %s" % logic_red_lowest_rate)
        print("--------")
        print("base_sell_hightest_price: %s | curr_buy_highest_price: %s | green_highest_rate at the right time: %s" % (
            base_sell_hightest_price, curr_buy_lowest_price, green_highest_rate
        ))
        print("If you want get trade to be done, you should set the green rate higher than %s" % logic_green_highest_rate)

        print(green_highest_rate, logic_green_highest_rate, logic_red_lowest_rate, red_lowest_rate)





def test_main():
    while True:
        stg = RateStrategy(BASE_TYPE, "OTB")
        stg.papar_trade()



if __name__ == "__main__":
    argv = sys.argv
    if len(argv) <= 1:
        pass
    else:
        currency_types = [argv[1]]
    test_main()
