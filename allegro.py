"""
Name: Allegro the biggest price searcher
Author: Pawel Matejko
LastDateMod: 2020.10.29
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re

# TODO wchodzimy na strone www.allegro.pl
# 1. wpisujemy w wyszukiwarke Iphone 11
# 2. wybieramy kolor czarny
# 3. zliczamy ilość wyświetlonych telefonów na pierwszej stronie wyników i ilość prezentujemy w consoli
# 4. szukamy największej ceny na liście i wyświetlamy w konsoli
# 5. do największej ceny dodajemy 23% Jak będzie miał Pan/Pani gotowy skrypt, to proszę go wexportować lub wrzucić gdzieś do Gita i podać linka

def init_browser_edge():
    browser = webdriver.Edge(r"C:\Program Files (x86)\Microsoft\Edge Dev\Application\msedgedriver.exe")
    return browser


def go_to_allegro_main_page(browser):
    browser.get("https://allegro.pl")
    browser.refresh()


def init_browser():
    binary = FirefoxBinary(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')
    options = webdriver.FirefoxOptions()
    browser = webdriver.Firefox(firefox_binary=binary)
    return browser


def click_accept_terms(browser):
    browser.implicitly_wait(5)
    accept_terms_selector = r'button._13q9y:nth-child(2)'
    accept_terms = WebDriverWait(browser, 25).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, accept_terms_selector)))
    accept_terms.click()


def put_text_into_the_search_box(browser, phrase):
    element = browser.find_element_by_css_selector("input.mr3m_1")
    element.send_keys(phrase)
    # element.send_keys(Keys.ENTER)


def wait_until_url_change(func):
    """ Decorator
    When you apply filter or you want to change page, it is good to use this decorator
    """
    def function_wrapper(*arg, **kw):
        current_url = browser.current_url
        _function = func(*arg, **kw)
        WebDriverWait(browser, 15).until(EC.url_changes(current_url))
        return _function

    return function_wrapper


def apply_filter_for_single_color(browser, color):
    """
    You can apply filter by query, but it wouldnt be user interface test.
    """
    query = rf'&kolor={color}'
    url_page = browser.current_url
    url_with_color_filter = url_page + query
    browser.get(url_with_color_filter)


def get_search_info(browser):
    xpath_to_info = r'/html/body/div[2]/div[4]/div/div/div/div/div/div[2]/div[1]/div[4]/div/div/div/div[1]'
    element = browser.find_element_by_xpath(xpath_to_info)
    return (element.get_attribute("innerHTML"))


@wait_until_url_change
def click_first_searched_recommendation(browser):
    xpath = r'//*[@id="suggestion-0"]'
    WebDriverWait(browser, 25).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    url_to_first_searched_item = browser.find_element_by_xpath(xpath).get_attribute('href')
    browser.get(url_to_first_searched_item)


def click_filter_by_black_color(browser):
    selector = r'fieldset._1rj80:nth-child(12) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(1)'
    browser.find_element_by_css_selector(selector).click()


def get_number_of_phones_on_current_page(browser):
    xpath = r'/html/body/div[2]/div[4]/div/div/div/div/div/div[2]/div[1]/div[3]/div[1]/div/div/div[2]/div[1]/div/section/article'
    return len(browser.find_elements_by_xpath(xpath))


def get_prices_of_all_phones(browser):
    """
    :return: sorted [list] of prices in desc order from current page
    """
    xpath = r'/html/body/div[2]/div[4]/div/div/div/div/div/div[2]/div[1]/div[3]/div[1]/div/div/div[2]/div[1]/div/section/article[*]/div/div[2]/div[2]/div/div/span'
    elements_with_row_price_string = browser.find_elements_by_xpath(xpath)
    prices = []
    for element in elements_with_row_price_string:
        row_string = element.get_attribute("innerHTML").replace(' ', '')
        # print(row_string)
        regex = r'[0-9]+'
        results = re.findall(regex, row_string)
        price_before_comma = float(results[0])
        try:
            price_after_comma = float(results[1])
        except IndexError:
            price_after_comma = 0
        prices.append(round(price_before_comma + price_after_comma / 100, 2))
    prices.sort(reverse=True)
    # print(prices)
    return prices


def wait_until_page_reload_after_applied_filter(browser, info_before_filtered):
    a = 0
    while True:
        if a == 10:
            raise AssertionError('Page didnt apply filter, the searched value are the same')
        browser.implicitly_wait(10)
        try:
            info_after_filter = get_search_info(browser)
        except:
            a += 1
            browser.refresh()
            browser.implicitly_wait(10)
            info_after_filter = get_search_info(browser)
        if info_before_filtered != info_after_filter:
            break


browser = init_browser()
go_to_allegro_main_page(browser)
click_accept_terms(browser)
put_text_into_the_search_box(browser, phrase='Iphone 11')
click_first_searched_recommendation(browser)
# apply_filter_for_single_color(browser, color='czarny')
info_about_search_before_filtered = get_search_info(browser)  # filtered
click_filter_by_black_color(browser)
wait_until_page_reload_after_applied_filter(browser, info_before_filtered=info_about_search_before_filtered)

print(rf'On the first page we have: {round(get_number_of_phones_on_current_page(browser), 2)}zl phones (60 + additional promoted)')
prices = get_prices_of_all_phones(browser)
the_biggest_price = prices[0]
print('the biggest price is:', the_biggest_price, 'zl')
the_biggest_price_plus_23 = the_biggest_price * 1.23
print('with additional 23% we will get', round(the_biggest_price_plus_23, 2), 'zl')
