import os
import Utils

url = "https://otcbtc.com"

buy_suffix = "sell_offers?currency={curr_type}&fiat_currency=cny&payment_type=all"
sell_suffix = "buy_offers?currency={curr_type}&fiat_currency=cny&payment_type=all"

currency_types = ["ETH", "EOS", "OTB", "BIG", "BNB", "DEW", "GXS", "IOST", "KIN", "NAS",
                  "SWFTC", "TNB", "USDT"]

def main():
    real_url = os.path.join(url, buy_suffix).format(curr_type="EOS")
    rsp, cnt = Utils.Web.do_get(real_url)
    print rsp, cnt


def get_buy_lowest(rsp):
    found = False
    rsp_list = rsp.splitlines()
    for index, value in enumerate(rsp_list):
        if "recommend-card__price" in value:
            found = True
            break
    return float(rsp_list[index + 1].strip()) if found else 0.0


def get_sell_highest(rsp):
    return get_buy_lowest(rsp)



if __name__ == "__main__":
    main()