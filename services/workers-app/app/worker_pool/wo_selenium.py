from app.config import config
from app.utils import jsonparser
import time, os, json, pprint, ast, csv
import requests as r
import logging
from flask import current_app as app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException


from flask_restplus import Namespace, Resource, fields
worker = Namespace('workers', description='busy busy beee beee')

'''
This file contains the selenium worker for starting a session with the hub, and a library for actions that can be used
More functionality added everyday
'''
class SeleniumWorkerSession():
    # Connection to de Selenium Hub, which runs in a Docker container
    def __init__(self):
        self.driver = webdriver.Remote(
            command_executor=config['selenium']['hub'],
            desired_capabilities={
                "browserName": "chrome",
                "applicationName": "debug",
                'loggingPrefs': {'performance': 'ALL'}
            }
        )

    def __enter__(self):
        return self.driver

    def __call__(self):
        print("waarom doet hij dit niet")
        self.wait(5)

    def __exit__(self, type, value, traceback):
        self.driver.quit()
        app.logger.info('chrome session released')

class SeleniumTaskLibrary():
    def __init__(self, driver):
        self.driver = driver

    def url(self, data):
        result = self.driver.get(data['input'])
        return {"root_url": self.driver.current_url}

    def info(self, data):
        return {"info":{"title": self.driver.title, "url":self.driver.current_url}}

    def source(self, data):
        return {"source": self.driver.page_source}

    def xpath(self, data):
        try:
            if data['type'] == 'text':
                    elements = self.driver.find_elements_by_xpath(data['input'])
                    return {data['name']: [element.text for element in elements]}
            elif data['type'] == 'urls':
                    self.wait(2)
                    elements = self.driver.find_elements_by_xpath(data['input'])
                    response = {"urls": [self.grab_attribute(element, 'href') for element in elements]}
            elif data['type'] == 'click':
                    button = self.driver.find_elements_by_xpath(data['input'])
                    button[0].click()
                    self.wait(3)
                    response = {"next_page": self.driver.current_url}
            else:
                response = {"exception": "xpath type not defined"}

        except WebDriverException as err:
            app.logger.error(err)
            response = {"exception":str(err)}
        except Exception as err:
            app.logger.error(err)
            response = {"exception":str(err)}

        return response


    def grab_attribute(self, element, attribute):
        try:
            return element.get_attribute(attribute)
        except Exception as ex:
             return {"exception": str(ex)}


    def elements(self, atrribute):
        #elements_by
        pass

    def wait(self, sec):
        self.driver.implicitly_wait(sec)
        return {'wait': f'Waited {sec} seconds'}

    def pagination(self, data):
        button = self.driver.find_elements_by_xpath(data['input'])
        button[0].click()
        self.wait(5)
        return {"response": f"current url: {self.driver.current_url}"}

    def cookie(self, cookie):
        self.driver.add_cookie(cookie)

    def scroll_to(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def driver_performance_log(self):
        ## write hieruit halen?
        write_jsonfile(self.driver.get_log('performance'))
        print("written performance log to json file")
        return self.driver.get_log('performance')

class SeleniumGroupTasksLibrary:
    def __init__(self, driver):
        self.driver = driver
        self.Task = SeleniumTaskLibrary(self.driver)

    def vacancy_pages(self, recipe):
        '''
        WORK IN PROGRESS
        links = [{"id": int, "table_title": "", "location": "", "stuff" }] ### Dynamic for every usefull element in tablerow?
        '''
        pages = 40
        all_links = []
        next_page = None #default if something goes wrong
        page_counter = 1

        try:
            for ingredient in recipe:
                if ingredient['fieldname'] == 'start_url':
                    starting_page = ingredient

                elif ingredient['fieldname'] == 'vacancy_xc_path':
                    links_path = ingredient

                elif ingredient['fieldname'] == 'next_page_xc_path':
                    next_page = ingredient


            self.Task.url(starting_page)
            for page in range(pages):
                get_links = self.Task.xpath(links_path)
                if any(print(elem) in all_links for elem in get_links['urls']):
                    #print(f"all_links: {all_links}") # testing
                    #print(f"get_links: {get_links}") # testing
                    break

                if 'urls' in get_links: all_links.extend(get_links['urls'])
                if next_page['input'] is not None:
                    try:
                        button = self.driver.find_element_by_xpath(next_page['input'])
                        actions = ActionChains(self.driver)
                        actions.move_to_element(button).perform()
                        #body.send_keys(webdriver.common.keys.Keys.END) #hacky solution to go to bottom of the page
                        #button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, next_page['input'])))
                        #time.sleep(7)
                        to_next_page = self.Task.pagination(next_page)
                        page_counter += 1
                    except TimeoutException as err:
                        print('timeout!, last page?')
                        break

                    except ElementClickInterceptedException as err:
                        app.logger.error(err)
                        break
                else:
                    break

        except Exception as err:
            app.logger.error(err, exc_info=True)

        print(len(all_links))
        response = {'pagination': 'succes', 'data': {'links': all_links, 'number_of_links': len(all_links), 'number_of_pages': page_counter, 'root_url': starting_page['input']}}
        print(f"name: {starting_page['input']} #urls: {response['data']['number_of_links']} pages: {page_counter}")
        return response

    def table_row_info(self):
        pass


def SeleniumTaskHandler(message):
    module = message['event']['module']
    name = message['event']['name']
    recipes = message['recipes']
    results = "yolo"
    try:
        with SeleniumWorkerSession() as browser:
            Group = SeleniumGroupTasksLibrary(browser)
            browser.implicitly_wait(5)
            if module == 'actionchain':
                results = [getattr(Group, recipe['group_id'])(recipe['ingredients']) for recipe in recipes]
                results[0]['data'].update({'name':name})
                results = results[0]['data']

            elif module == 'singleton':
                Task = SeleniumTaskLibrary(browser)
                results = [getattr(Task, ingredient['method'])(ingredient['data']) for ingredient in recipes]
                    ## Iets voor result bedenken wat het zijn nu losse dicts in lijst. dict comprehension mebe
    except Exception as err:
        app.logger.error(err, exc_info=True)
        results = str(err)
    finally:
        print('shutdown?')
    return {'response_selenium': {'results':results}}


### voor snelle dev tests
@worker.route('/test')
class SeleniumAPI(Resource):

    def get(self):
        message = {
            'event': {'method': 'requesting_workers', 'workers':['selenium'], 'name':'google', 'module': 'singleton'}, ### can be different
                'recipes': [
                    {'method': 'url', 'name': 'url', 'data': {'input': 'https://google.nl'}},
                    {'method': 'wait', 'data': 100}
                ]}

        response = SeleniumTaskHandler(message)
        return response



'''

Finding Elements:

# find_element_by_id
# find_element_by_name
# find_element_by_xpath
# find_element_by_link_text
# find_element_by_partial_link_text
# find_element_by_tag_name
# find_element_by_class_name
# find_element_by_css_selector”


Looking if elements are present:

element_located_selection_state_to_be(locator, is_selected): checks whether an element is located matching a locator (see explanation below) and its selection state matches is_selected (True of False).”
element_located_to_be_selected(locator): checks whether an element (a WebElement object) is located matching a locator (see explanation below) and is selected.
element_selection_state_to_be(element, is_selected): checks whether the selection state of an element (a WebElement object) matches is_selected (True or False).
element_to_be_selected(element): checks whether an element (a WebElement object) is selected.
element_to_be_clickable(locator): checks whether an element is located matching a locator (see explanation below) and can be clicked (i.e., is enabled).
frame_to_be_available_and_switch_to_it(locator): checks whether a frame matching a locator (see explanation below) is located and can be switched to, once found, the condition switches to this frame.
invisibility_of_element_located(locator): checks whether an element matching a locator (see explanation below) is invisible or not present on the page (visibility means that the element is not only displayed or has a height and width that is greater than 0).
presence_of_all_elements_located(locator): checks whether there is at least one element present on the page matching a locator (see explanation below). If found, the condition returns a list of matching elements .
presence_of_element_located(locator): checks whether there is at least one element present[…]
visibility_of(element): checks whether a present element (a WebElement object) is visible (visibility means that the element is not only displayed but also has a height and width that is greater than 0).
visibility_of_all_elements_located(locator): checks whether all elements matching a locator (see explanation below) are also visible. If this is the case, returns a list of matching elements.
visibility_of_any_elements_located(locator): checks whether any element matching a locator (see explanation below) is visible. If this is the case, returns the first visible element.
visibility_of_element_located(locator): checks whether the first element matching a locator (see explanation below) is also visible. If this is the case, return the element.


Windows & url changes:
alert_is_present: checks whether an alert is present.
new_window_is_opened(current_handles): checks whether a new window has opened.
number_of_windows_to_be(num_windows): checks whether a specific number of windows have opened.
title_contains(title): checks whether the title of the page contains the given string.
title_is(title): checks whether the title of the page is equal to the given string.
url_changes(url): checks whether the URL is different from a given one.
url_contains(url): checks whether the URL contains the given one.
url_matches(pattern): checks whether the URL matches a given regular expression pattern.
url_to_be(url): checks whether the URL matches the given one .


Dropdown menus:
select_by_index(index): select the option at the given index.
select_by_value(value): select all options that have a value matching the argument.
select_by_visible_text(text): select all options that display text matching the argument.
The methods above all come with deselect_* variants as well to deselect options. The deselect_all method clears all selected entries (note that the select tag can support multiple selections).
all_selected_options: returns a list of all selected options belonging to this select tag.
first_selected_option: the first selected option in this select tag (or the currently selected option in a normal select that only allows for a single selection).
options: returns a list of all options belonging to this select tag.”

Simulate Clicks:
click(on_element=None): clicks an element. If None is given, uses the current mouse position.
click_and_hold(on_element=None): holds down the left mouse button on an element or the current mouse position.
release(on_element=None): releasing a held mouse button on an element or the current mouse position.
context_click(on_element=None): performs a context click (right-click) on an element or the current mouse position.
double_click(on_element=None): double-clicks an element or the current mouse position.

Moving on the screen:
move_by_offset(xoffset, yoffset): move the mouse to an offset from current mouse position.
move_to_element(to_element): move the mouse to the middle of an element.
move_to_element_with_offset(to_element, xoffset, yoffset): move the mouse by an offset of the specified element. Offsets are relative to the top-left corner of the element.
drag_and_drop(source, target): holds down the left mouse button on the source element, then moves to the target element and releases the mouse button .
drag_and_drop_by_offset(source, xoffset, yoffset): holds down the left mouse button on the source element, then moves to the target offset and releases the mouse button.
key_down(value, element=None): sends a keypress only, without releasing it. Should only be used with modifier keys (i.e., Control, Alt, and Shift).
key_up[…]
key_up(value, element=None): releases a modifier key.
send_keys(*keys_to_send): sends keys to current focused element.
send_keys_to_element(element, *keys_to_send): sends keys to an element.
pause(seconds): wait for a given amount of seconds.

Action chaining:
perform(): performs all stored actions defined on the action chain. This is normally the last command you’ll give to a chain.
reset_actions(): clears actions that are already stored on the remote end.”



'''

### temp THE FRANKENCODE
#### Implement GROUP OF TASKS
def vacancy_parser(message):
    recipes = message['event']['recipes']
    name = message['event']['name']
    page_counter = 0
    end_of_pages = True
    all_links = []
    with SeleniumWorkerSession() as browser:
        Task = SeleniumTaskLibrary(browser)
        for recipe in recipes:

            if recipe['group_id'] == 'start':
                for ingredient in recipe['ingredients']:
                    starter = Task.url(ingredient['data'])
                    print("begonnen op:", starter)
            if recipe['group_id'] == 'all_links':
                while end_of_pages:
                    print(page_counter + 1)
                    if 'next_page' in recipe:
                        print(name)
                        end_of_pages = False
                    links = [getattr(Task, ingredient['method'])(ingredient['data']) for ingredient in recipe['ingredients'] if recipe['group_id'] == 'all_links']
                    page_counter += 1
                    if links != []:
                        if any(elem in all_links for elem in links[0]['urls']):
                            end_of_pages = False

                        #print(links)
                        if any('EXCEPTION' in x for x in links):
                            print('EXCEPTION')
                            end_of_pages = False

                        if page_counter == 50:
                            end_of_pages = False
                    #print('ree', links)
                        else:
                            all_links.extend(links[0]['urls'])
    number_of_links = len(all_links)
    response = {'number_of_pages': page_counter, 'number_of_links': number_of_links,'links': all_links}
    response.update(starter)
    response.update({'name':name})
    return response
