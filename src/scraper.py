from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
import urllib.parse
from selenium.webdriver.common.by import By
from bose import BaseTask, Wait, Output
import time
import lxml.html as html


def write(result):
    print(f'result:\n\n\n------------------\n{Colortext.OKBLUE}{result}{Colortext.END}')
    # Output.write_finished(result)
    # Output.write_csv(result, "finished.csv")


def do_filter(ls, filter_data):
    def fn(i):
        min_rating = filter_data.get("min_rating")
        min_reviews = filter_data.get("min_reviews")
        is_kosher = filter_data.get("is_kosher", False)
        is_car = filter_data.get("is_car", False)
        has_phone = filter_data.get("has_phone")
        has_website = filter_data.get("has_website")

        rating = i.get('rating')
        number_of_reviews = i.get('number_of_reviews')
        title = i.get("title")
        category = i.get("category")
        web_site = i.get("website")
        phone = i.get("phone")

        if min_rating is not None:
            if rating == '' or rating is None or rating < min_rating:
                return False

        if min_reviews is not None:
            if number_of_reviews == '' or number_of_reviews is None or number_of_reviews < min_reviews:
                return False

        if is_kosher:
            if 'kosher' in category.lower() or 'jew' in category.lower() or 'kosher' in title.lower() or 'jew' in title.lower():
                pass
            else:
                return False

        if has_website is not None:
            if not has_website:
                if web_site is not None:
                    return False

        if has_phone is not None:
            if has_phone:
                if phone is None or phone == '':
                    return False

        if is_car:
            if 'car' in category.lower() or 'car' in title.lower():
                pass
            else:
                return False

        return True

    return list(filter(fn, ls))


class Colortext:
    # Foreground:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    # Formatting
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # End colored text
    END = '\033[0m'
    NC = '\x1b[0m'  # No Color


class Task(BaseTask):
    GET_FIRST_PAGE = False
    queries = [
    ]
    global scroll_times

    def run(self, driver):
        c = 0
        while True:
            try:
                def str_week_to_dct(dict_data: dict, week_text):
                    split_list = ['Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
                    if week_text is not None:
                        week_text = week_text.replace('PM-', ' P*M-')
                        week_text = week_text.replace('PM', ' PM | ')
                        week_text = week_text.replace('P*M-', ' PM - ')
                        week_text = week_text.replace('AM–', ' A*M-')
                        week_text = week_text.replace('AM', ' AM | ')
                        week_text = week_text.replace('A*M-', ' AM - ')
                        week_text = week_text.replace('Closed', 'Closed | ')
                        week_text = week_text.replace(' | ', ',')
                        cz = week_text.split(',')
                        count_week = []
                        list(map(lambda l: list(map(lambda cw: count_week.append(
                            str(cw).replace(l, f'{l}:').replace('\u202f', '')) if l in cw else None, cz)), split_list))
                        list(map(lambda dc: dict_data.update({str(dc).split(':')[0]: str(dc).split(':')[1]}),
                                 count_week))
                    else:
                        list(map(lambda dc: dict_data.update({dc: ''}), split_list))

                def get_links(query, sc_time):
                    def scroll_till_end(times):
                        global has_scrolled

                        def visit_gmap():

                            endpoint = f'maps/search/{urllib.parse.quote_plus(query)}'
                            url = f'https://www.google.com/{endpoint}?hl=en'

                            driver.get_by_current_page_referrer(url)

                            if not driver.is_in_page(endpoint, Wait.LONG * 3):
                                print('Revisiting')
                                visit_gmap()

                        visit_gmap()
                        # change to eng
                        # time.sleep(2)
                        # menu_button = driver.find_elements(By.CSS_SELECTOR, ".wR3cXd.jHfBQd")
                        # menu_button[0].click()
                        # time.sleep(2)
                        # lan_button = driver.find_elements(By.CSS_SELECTOR, ".aAaxGf.T2ozWe")
                        # lan_button[0].click()

                        # main
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

                                end_el = driver.get_element_or_none_by_text_contains("You've reached the end of the "
                                                                                     "list.", Wait.SHORT)
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

                    scroll_till_end(sc_time)

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

                        out_dict['address'] = get_el_text(
                            driver.get_element_or_none("//button[@data-item-id='address']"))
                        out_dict['website'] = get_el_text(driver.get_element_or_none("//a[@data-item-id='authority']"))
                        out_dict['phone'] = get_el_text(
                            driver.get_element_or_none("//button[starts-with(@data-item-id,'phone:tel:')]"))
                        # out_dict['open_days'] = get_el_text(driver.get_element_or_none("//div[@data-item-id='875']"))

                        tmp_elem = driver.get_element_or_none_by_selector(".RZ66Rb.FgCUCc img")
                        image_gall = driver.find_elements(By.CLASS_NAME, "DaSXdd")
                        merged_img = "" if len(
                            image_gall) == 0 else f"{image_gall[0].get_attribute('src')};{image_gall[-2].get_attribute('src')};{image_gall[-1].get_attribute('src')}"

                        # click to view days
                        time.sleep(2)
                        time_list = driver.get_element_or_none_by_selector(".eK4R0e.fontBodyMedium")
                        back = False
                        if time_list is None:
                            # click opened days
                            back = True
                            open_time = driver.find_elements(By.XPATH, "//button[@class='CsEnBe']")
                            lsc = list(
                                map(lambda n_n: {str(n_n): open_time[n_n].get_attribute("aria-label")}, range(0, 4)))
                            print('open time is none->:\t', lsc)
                            lsc = list(map(lambda n_n: n_n if 'See more hours' in open_time[n_n].get_attribute(
                                "aria-label") else None, range(0, 4)))
                            lsc = list(filter(lambda f: f is not None, lsc))
                            n = lsc[0]
                            driver.implicitly_wait(10)
                            ActionChains(driver).move_to_element(open_time[n]).click(open_time[n]).perform()
                        time.sleep(2)
                        time_list = driver.get_element_or_none_by_selector(".eK4R0e.fontBodyMedium")
                        if time_list is not None:
                            time_list = time_list.get_attribute('innerHTML')
                            time_text = html.fromstring(time_list)
                            str_week_to_dct(dict_data=out_dict, week_text=time_text.text_content())
                            # print('\n\n\ntime list:\t', time_text.text_content(), '\n\n\n')
                        else:
                            str_week_to_dct(dict_data=out_dict, week_text=time_list)

                        time.sleep(2)
                        if back:
                            # back_btn = driver.find_elements(By.CSS_SELECTOR, '.VfPpkd-icon-LgbsSe.yHy1rc.eT1oJ.mN1ivc')
                            back_btn = driver.find_elements(By.XPATH, '//button[@aria-label="Back"]')
                            back_btn[0].click()

                        # click sharing modal
                        time.sleep(2)
                        sharing = driver.find_elements(By.CSS_SELECTOR, ".g88MCb.S9kvJb")
                        sharing[4].click()
                        time.sleep(4)
                        # share_link = driver.find_element(By.XPATH, "//input[@class='vrsrZe']")
                        # //*[contains(text(), 'My Button')]
                        # map_button = driver.find_element(By.XPATH, "//button[@class='zaxyGe L6Bbsd YTfrze']")
                        map_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Embed a map')]")
                        map_button.click()
                        time.sleep(2)
                        embed_link = driver.find_element(By.XPATH, "//input[@class='yA7sBe']")
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        if tmp_elem is not None:
                            # out_dict['img_link'] = tmp_elem.get_attribute("src")
                            out_dict['img_link'] = merged_img

                        out_dict['link'] = link
                        out_dict['embed_frame'] = embed_link

                        # comments
                        find_commenters = driver.find_elements(By.CLASS_NAME, 'd4r55')
                        find_comment = driver.find_elements(By.CLASS_NAME, 'wiI7pd')
                        find_comment_rate = driver.find_elements(By.CLASS_NAME, 'kvMYJc')
                        list(map(lambda cm_n:
                                 out_dict.update({
                                     f'Review_Name_{cm_n + 1}': find_commenters[cm_n].get_attribute('textContent'),
                                     f'Review_Rate_{cm_n + 1}': find_comment_rate[cm_n].get_attribute('aria-label'),
                                     f'Review_Comment_{cm_n + 1}': find_comment[cm_n].get_attribute('textContent')
                                 })
                                 , range(3)))
                        if out_dict['title'] == 'Dante Kitchen & Bar': print(out_dict)

                        return out_dict

                    ls = list(map(get_data, links))
                    return ls

                queries = self.queries

                def get_data(sc_time):
                    result = []
                    max_listings = 10000

                    driver.get_google()

                    for q in queries:
                        links = get_links(q, sc_time)

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

                result = get_data(self.scroll_times)
                write(result)
                break
            except ValueError as e:
                c += 1
                if c > 0:
                    print(f'please fix error {e}')
                    break
                else:
                    print("Low internet, trying again")
