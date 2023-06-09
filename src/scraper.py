from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
import urllib.parse
from selenium.webdriver.common.by import By
from bose import BaseTask, Wait, Output
import time


def write(result):
    Output.write_finished(result)
    Output.write_csv(result, "finished.csv")


def do_filter(ls, filter_data):
    def fn(i):
        min_rating = filter_data.get("min_rating")
        min_reviews = filter_data.get("min_reviews")
        is_kosher = filter_data.get("is_kosher", False)
        is_car = filter_data.get("is_car", False)
        has_phone = filter_data.get("has_phone")
        has_website = filter_data.get("has_website")
        open_days = filter_data.get("open_days")

        rating = i.get('rating')
        number_of_reviews = i.get('number_of_reviews')
        title = i.get("title")
        category = i.get("category")
        web_site = i.get("website")
        phone = i.get("phone")
        opdays = i.get("open_days")

        if min_rating != None:
            if rating == '' or rating is None or rating < min_rating:
                return False

        if min_reviews != None:
            if number_of_reviews == '' or number_of_reviews is None or number_of_reviews < min_reviews:
                return False

        if is_kosher:
            if 'kosher' in category.lower() or 'jew' in category.lower() or 'kosher' in title.lower() or 'jew' in title.lower():
                pass
            else:
                return False

        if has_website is not None:
            if has_website == False:
                if web_site is not None:
                    return False

        if has_phone is not None:
            if has_phone == True:
                if phone is None or phone == '':
                    return False

        if open_days is not None:
            if open_days:
                if opdays is None or opdays == '':
                    return False

        if is_car:
            if 'car' in category.lower() or 'car' in title.lower():
                pass
            else:
                return False

        return True

    return list(filter(fn, ls))


class Task(BaseTask):
    GET_FIRST_PAGE = False
    queries = [
        "Amsterdam, restaurant",
    ]

    def run(self, driver):
        def get_links(query):
            def scroll_till_end(times):
                global has_scrolled

                def visit_gmap():

                    endpoint = f'maps/search/{urllib.parse.quote_plus(query)}'
                    url = f'https://www.google.com/{endpoint}'

                    driver.get_by_current_page_referrer(url)

                    if not driver.is_in_page(endpoint, Wait.LONG * 3):
                        print('Revisiting')
                        visit_gmap()

                visit_gmap()
                ci = 0  # count scroll
                while True:
                    el = driver.get_element_or_none_by_selector('[role="feed"]', Wait.LONG)

                    if el is None:
                        visit_gmap()
                        print('sc-ing')
                        return scroll_till_end(times + 1)
                    else:
                        # for i in range(0, 5):
                        #     has_scrolled = driver.scroll_element(el)
                        has_scrolled = driver.scroll_element(el)

                        end_el = driver.get_element_or_none_by_text_contains("You've reached the end of the list.", Wait.SHORT)
                        if end_el is not None:
                            driver.scroll_element(el)
                            return

                        if not has_scrolled:
                            driver.sleep(0.1)
                            print('not Scrolling...')
                        else:
                            ci += 1
                            print(f'Scrolling {ci} times...')
                        if self.GET_FIRST_PAGE or ci == times:
                            return

            scroll_till_end(1)

            def extract_links(elements):
                def extract_link(el):
                    return el.get_attribute("href")

                return list(map(extract_link, elements))

            els = driver.get_elements_or_none_by_selector('[role="feed"]  [role="article"] > a', Wait.SHORT)
            links = extract_links(els)

            Output.write_pending(links)

            print('Done Filter')

            return links

        def get_maps_data(links):
            def get_data(link):

                driver.get_by_current_page_referrer(link)

                tmp_elem = driver.get_element_or_none("//div[@class='TIHn2']", Wait.SHORT)
                out_dict = {}
                heading = driver.get_element_or_none_by_selector('h1', Wait.SHORT)

                if heading is not None:
                    out_dict['title'] = heading.text

                else:
                    out_dict['title'] = ''

                rating = driver.get_element_or_none_by_selector('div.F7nice', Wait.SHORT)

                if rating is not None:
                    val = rating.text
                else:
                    val = None

                if (val is None) or (val == ''):
                    out_dict['rating'] = None
                    out_dict['number_of_reviews'] = None
                else:
                    out_dict['rating'] = float(val[:3].replace(',', '.'))
                    num = ''
                    for c in val[3:]:
                        if c.isdigit():
                            num = num + c
                    if len(num) > 0:
                        out_dict['number_of_reviews'] = int(num)
                    else:
                        out_dict['number_of_reviews'] = None

                category = driver.get_element_or_none_by_selector(
                    'button[jsaction="pane.rating.category"]')
                out_dict['category'] = '' if category is None else category.text
                tmp_elem = driver.get_element_or_none("//div[@class='m6QErb']")

                def get_el_text(el):
                    if el is not None:
                        return el.text
                    return ''

                out_dict['address'] = get_el_text(driver.get_element_or_none("//button[@data-item-id='address']"))
                out_dict['website'] = get_el_text(driver.get_element_or_none("//a[@data-item-id='authority']"))
                out_dict['phone'] = get_el_text(driver.get_element_or_none("//button[starts-with(@data-item-id,'phone:tel:')]"))
                out_dict['open_days'] = get_el_text(driver.get_element_or_none("//div[@data-item-id='875']"))

                tmp_elem = driver.get_element_or_none_by_selector(".RZ66Rb.FgCUCc img")
                image_gall = driver.find_elements(By.CLASS_NAME, "DaSXdd")
                merged_img = "" if len(image_gall) == 0 else f"{image_gall[0].get_attribute('src')};{image_gall[-2].get_attribute('src')};{image_gall[-1].get_attribute('src')}"

                sharing = driver.find_elements(By.CSS_SELECTOR, ".g88MCb.S9kvJb")
                sharing[4].click()
                # click to view days
                time.sleep(3)
                opened_days = driver.find_element(By.XPATH, "//button[@class='CsEnBe']")
                opened_days.click()
                time.sleep(2)
                time_list = driver.get_element_or_none_by_selector(".eK4R0e.fontBodyMedium tbody")
                time_list = time_list.text
                print('\n\n\ntime list:\t', time_list, '\n\n\n')
                time.sleep(4)
                # share_link = driver.find_element(By.XPATH, "//input[@class='vrsrZe']")
                map_button = driver.find_element(By.XPATH, "//button[@class='zaxyGe L6Bbsd YTfrze']")
                map_button.click()
                time.sleep(2)
                embed_link = driver.find_element(By.XPATH, "//input[@class='yA7sBe']")
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                if tmp_elem is not None:
                    # out_dict['img_link'] = tmp_elem.get_attribute("src")
                    out_dict['img_link'] = merged_img

                out_dict['link'] = link
                out_dict['embed_frame'] = embed_link

                print(out_dict)

                return out_dict

            ls = list(map(get_data, links))
            return ls

        queries = self.queries

        def get_data():
            result = []
            max_listings = 10000

            driver.get_google()

            for q in queries:
                links = get_links(q)

                print(f'Fetched {len(links)} links.')

                filter_data = {
                    # "min_reviews": 1,
                    # "has_phone": True,
                }

                a = get_maps_data(links)
                new_results = do_filter(a, filter_data)

                print(f'Filtered {len(new_results)} links from {len(a)}.')

                result = result + new_results
                # write(result)
                if len(result) > max_listings:
                    return result

            return result

        result = get_data()
        write(result)
