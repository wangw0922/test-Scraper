import re

from project.Collect.src.get_response import get_response
from parsel import Selector


def get_add_cart_info(sel):
    """
    Get add cart info of product
    """
    add_cart_info = ""
    try:
        info_one = sel.xpath('//*[@id="gestalt_feature_div"]/div[1]/span/text()').get().strip() + " "
        add_cart_info += info_one
        info_two = sel.xpath('//*[@id="gestalt-popover-button-announce"]/text()').get().strip() + " "
        add_cart_info += info_two
        info_three = sel.xpath('//*[@id="gestalt_feature_div"]/div[2]/span/text()').get().strip() + " "
        add_cart_info += info_three
    except:
        pass
    return add_cart_info


def get_second_brand(response):
    """
    Get second brand of product
    """
    import re
    try:
        second_brand = re.search("Visit the(.+)Store", response).group(1).strip()
    except:
        second_brand = ""
    return second_brand

def get_changed_asin(html):
    asin = re.search('asin: "(.+?)"', html).group(1).strip()
    return asin


url = "https://www.amazon.com/dp/B099F7BY52"

resp = get_response(url)
asin = get_changed_asin(resp.text)
print(asin)



