#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Gabriel Jordão <gabrielpjordao@gmail.com>
# Copyright (C) 2012 Osvaldo Matos-Junior <tupy@jusbrasil.com.br>
#
# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.opensource.org/licenses/osl-3.0.php
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

splinter_available = True
try:
    import splinter
    from splinter.driver import webdriver

except ImportError:
    splinter_available = False

lxml_available = True
try:
    import lxml
    from lxml.html import tostring
except ImportError:
    lxml_available = False

from pyccuracy.drivers import BaseDriver, DriverError
from selenium_element_selector import *
from selenium.common.exceptions import StaleElementReferenceException

class SplinterDriver(BaseDriver):
    backend = 'splinter'

    def __init__(self, context, browser=None):
        self.context = context
        self.browser = browser

    def start_test(self, url=None):
        if not splinter_available:
            raise RuntimeError('You *MUST* have splinter installed to use this driver')

        if not url:
            url = self.context.settings.base_url
        self.start_splinter(url)

    def start_splinter(self, url):
        browser_to_run = self.context.settings.browser_to_run

        if not self.browser:
            if browser_to_run == 'chrome':
                # Chrome doesn't support maximize_window()
                from selenium.webdriver.chrome.options import Options
                options = Options()
                options.add_argument('--start-maximized')
                self.browser = splinter.Browser(browser_to_run, chrome_options=options)
            else:
                self.browser = splinter.Browser(browser_to_run)
                self.browser.driver.maximize_window()

        self.page_open(url)

    def stop_test(self):
        self.stop_selenium()

    def stop_selenium(self):
        self.browser.quit()

    def resolve_element_key(self, context, element_type, element_key):
        if not context:
            return element_key
        return SeleniumElementSelector.element(element_type, element_key)

    def page_open(self, url):
        """
        Note: it not uses the visit method from splinter instead in order to
        override the current behavior of it, which is, raising an error while
        visiting pages with error status codes
        """
        self.browser.connect(url)
        self.browser.driver.get(url)

    def go_back(self):
        self.browser.back()
        self.wait_for_page()

    def refresh(self):
        self.browser.reload()
        self.wait_for_page()

    def wait_for_page(self, timeout=30000):
        while self.browser.evaluate_script('document.readyState') != 'complete':
            time.sleep(0.05)

    def click_element(self, element_selector):
        element = self.browser.find_by_xpath(element_selector)
        element.click()

    def get_title(self):
        return self.browser.title

    def is_element_visible(self, element_selector):

        element = self.browser.find_by_xpath(element_selector)

        if element:
            try:
                return element.visible
            except StaleElementReferenceException:
                """
                This happens because sometimes, while code is being execcuted,
                the element can be removed from the DOM. Causing this exception.
                In this case, we assume that the element is not visible, returning
                False
                """
                return False
        return False

    def is_element_enabled(self, element):
        script = """this.page().findElement("%s").disabled;"""

        script_return = self.browser.evaluate_script(script % element)
        if script_return == "null":
            is_disabled = self.__get_attribute_value(element, "disabled")
        else:
            is_disabled = script_return[0].upper()=="T" # is it 'True'?
        return not is_disabled

    def wait_for_element_present(self, element_selector, timeout):
        elapsed = 0
        interval = 0.5

        while (elapsed < timeout):
            elapsed += interval
            if self.is_element_visible(element_selector):
                return True
            time.sleep(interval)

        return False

    def wait_for_element_to_disappear(self, element_selector, timeout):
        elapsed = 0
        interval = 0.2

        while (elapsed < timeout):
            elapsed += interval
            if not self.is_element_visible(element_selector):
                return True
            time.sleep(interval)

        return False

    def get_element_text(self, element_selector):
        text = ''

        element = self.browser.find_by_xpath(element_selector)
        properties = {
                        'input' : 'value',
                        'textarea' : 'value',
                     }
        try:
            text = getattr(element, properties.get(element.tag_name, 'text'))
        except KeyError, err:
            raise err

        return text

    def get_element_markup(self, element_selector):
        if not lxml_available:
            raise RuntimeError("You can't use markup actions unless you install lxml.")

        root = lxml.etree.HTML(self.get_html_source())
        element = root.xpath(element_selector)
        if len(element) > 1:
            raise RuntimeError("There is more than one element selected by the selector passed.")
        return tostring(element[0], encoding='unicode')

    def mouseover_element(self, element_selector):
        element = self.browser.find_by_xpath(element_selector)
        element.mouse_over()

    def mouseout_element(self, element_selector):
        element = self.browser.find_by_xpath(element_selector)
        element.mouse_out()

    def checkbox_is_checked(self, checkbox_selector):
        element = self.browser.find_by_xpath(checkbox_selector)
        return element.checked

    def checkbox_check(self, checkbox_selector):
        element = self.browser.find_by_xpath(checkbox_selector)
        element.check()

    def checkbox_uncheck(self, checkbox_selector):
        element = self.browser.find_by_xpath(checkbox_selector)
        element.uncheck()

    def get_selected_text(self, element_selector):
        element = self.browser.find_by_xpath(element_selector)
        return element.value

    def select_option_by_index(self, element_selector, index):
        return self.__select_option(element_selector, "index", index)

    def select_option_by_value(self, element_selector, value):
        return self.__select_option(element_selector, "value", value)

    def select_option_by_text(self, element_selector, text):
        return self.__select_option(element_selector, "label", text)

    def get_select_options(self, element_selector):
        element = self.browser.find_by_xpath(element_selector)
        options = element.find_by_tag('option')
        return [opt.text for opt in options]

    def __select_option(self, element_selector, option_selector, option_value):

        try:
            error_message = "Option with %s '%s' not found" % (option_selector, option_value)
            element = self.browser.find_by_xpath(element_selector)
            options = element.find_by_tag('option')
            for o in options:
                if o.value == option_value:
                    o._element.click()
                    break
        except Exception, error:
            if error.message == error_message:
                return False
            else:
                raise
        return True

    def is_element_empty(self, element_selector):
        current_text = self.get_element_text(element_selector)
        return current_text == ""

    def get_image_src(self, image_selector):
        return self.__get_attribute_value(image_selector, "src")

    def type_text(self, input_selector, text):
        element = self.browser.find_by_xpath(input_selector)
        element.type(text)

    def type_keys(self, input_selector, text):
        element = self.browser.find_by_xpath(input_selector)
        element.type(text, slowly=True)

    def exec_js(self, js):
        return self.browser.execute_script(js)

    def clean_input(self, input_selector):
        self.type_text(input_selector, "")

    def get_link_href(self, link_selector):
        return self.__get_attribute_value(link_selector, "href")

    def get_html_source(self):
        return self.browser.evaluate_script("document.getElementsByTagName('html')[0].innerHTML")

    def get_xpath_count(self, xpath):
        elements = self.browser.find_by_xpath(xpath)
        return len(elements)

    def get_dialog_text(self):
        alert = self.browser.get_alert()
        return alert.text

    def accept_dialog(self):
        alert = self.browser.get_alert()
        alert.accept()

    def dismiss_dialog(self):
        alert = self.browser.get_alert()
        alert.dismiss()

    def __get_attribute_value(self, element_selector, attribute):
        try:
            element = self.browser.find_by_xpath(element_selector)
            if isinstance(element, list):
                element = element[0]
            attr_value = element[attribute]
        except Exception, inst:
            if "Could not find element attribute" in str(inst):
                attr_value = None
            else:
                raise
        return attr_value

        def __str__(self):
            return self.__unicode__()

    def __unicode__(self):
        return "Splinter Driver using %s" % self.context.settings.browser_to_run
