#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Gabriel Jordão <gabrielpjordao@gmail.com>
# Copyright (C) 2009 Osvaldo Matos Junior <tupy@jusbrasil.com.br>
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

import unittest

from mocker import Mocker

from pyccuracy.common import Context, Settings
from pyccuracy.drivers import DriverError
from pyccuracy.drivers.core.splinter_driver import SplinterDriver

class SplinterDriverTest(unittest.TestCase):

    def test_can_create_splinter_browser_driver(self):
        context = Context(Settings())
        driver = SplinterDriver(context)

        assert driver is not None

    def test_splinter_driver_keeps_context(self):
        context = Context(Settings())
        driver = SplinterDriver(context)

        self.assertEqual(driver.context, context)

    def test_splinter_driver_overrides_start_test_properly(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.connect('http://localhost')
        browser_mock.driver.get('http://localhost')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.start_test("http://localhost")

    def test_splinter_calls_quit_method_properly(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()
        browser_mock.quit()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)

            driver.stop_test()

    def test_splinter_driver_visits_page_properly(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.connect('http://localhost')
        browser_mock.driver.get('http://localhost')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)

            driver.page_open("http://localhost")

    def test_splinter_driver_waits_correctly_for_page_loading(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.evaluate_script('document.readyState')
        mocker.result('notComplete')

        browser_mock.evaluate_script('document.readyState')
        mocker.result('complete')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)

            driver.wait_for_page()

    def test_splinter_driver_calls_click_from_an_element_properly(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()
        browser_mock.find_by_xpath('//div')

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.click()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)

            driver.click_element("//div")

    def test_splinter_driver_gets_title_from_splinter_properly(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()
        browser_mock.title
        mocker.result('Some title')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)

            title = driver.get_title()
            self.assertEqual(title, "Some title")

    def test_splinter_driver_calls_get_eval(self):

        mocker = Mocker()

        javascript = "some javascript"
        context = Context(Settings())
        browser_mock = mocker.mock()
        browser_mock.execute_script(javascript)
        mocker.result("ok")

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)

            assert driver.exec_js(javascript) == "ok"

    def test_splinter_driver_calls_type_keys(self):

        mocker = Mocker()

        input_selector = "//some_xpath"
        text = "text to type"
        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.find_by_xpath(input_selector)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.type(text, slowly=True)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.type_keys(input_selector, text)

    def test_splinter_driver_calls_type_text(self):

        mocker = Mocker()

        input_selector = "//some_xpath"
        text = "text to type"
        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.find_by_xpath(input_selector)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.type(text)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.type_text(input_selector, text)

    def test_wait_for_presence(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        element_mock = mocker.mock()

        browser_mock.find_by_xpath('some element')
        mocker.result([])

        element_mock = mocker.mock()

        browser_mock.find_by_xpath('some element')
        mocker.result(element_mock)

        element_mock.visible
        mocker.result(True)


        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.wait_for_element_present("some element", 1)

    def test_wait_for_disappear(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()
        browser_mock.find_by_xpath('some element')
        mocker.count(min=1, max=None)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.visible
        mocker.result(True)

        mocker.count(min=1, max=None)
        mocker.result(True)

        element_mock.visible
        mocker.result(False)
        mocker.count(min=2, max=None)

        mocker.result(True)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.wait_for_element_to_disappear("some element", 1)

    def test_get_element_markup(self):

        mocker = Mocker()
        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.evaluate_script("document.getElementsByTagName('html')[0].innerHTML")

        html_mock = """<div>Tes<b>t</b>e</div><span>NotTheDiv</span>"""

        mocker.result(html_mock)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            self.assertEqual(driver.get_element_markup('//div'), u'<div>Tes<b>t</b>e</div>')

    def test_xpath_count_returns_the_correct_list_size(self):

        mocker = Mocker()
        context = Context(Settings())
        browser_mock = mocker.mock()
        xpath = '//div'

        browser_mock.find_by_xpath(xpath)
        elements_list_mock = [1,2,3]
        mocker.result(elements_list_mock)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            self.assertEqual(driver.get_xpath_count(xpath), len(elements_list_mock))

    def test_splinter_driver_mouse_over(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.mouse_over()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.mouseover_element(xpath)

    def test_splinter_driver_mouse_out(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.mouse_out()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.mouseout_element(xpath)

    def test_splinter_driver_check_checkbox_is_checked(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.checked
        mocker.result(True)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            is_checked = driver.checkbox_is_checked(xpath)
            self.assertEqual(is_checked, True)

    def test_splinter_driver_check_checkbox_action(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.check()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.checkbox_check(xpath)

    def test_splinter_driver_uncheck_checkbox_action(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock.uncheck()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.checkbox_uncheck(xpath)

    def test_splinter_get_link_href(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//a'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)

        _link = 'mylink.html'

        element_mock['href']
        mocker.result(_link)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            element_link = driver.get_link_href(xpath)
            self.assertEqual(_link, element_link)

    def test_splinter_check_element_enable_with_disabled_element(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'
        script = 'this.page().findElement("%s").disabled;' % xpath

        browser_mock.evaluate_script(script)
        mocker.result('true')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            is_enabled = driver.is_element_enabled(xpath)
            self.assertEqual(is_enabled, False)

    def test_splinter_check_element_enable_with_disabled_element(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'
        script = 'this.page().findElement("%s").disabled;' % xpath

        browser_mock.find_by_xpath(xpath)
        element_mock = mocker.mock()
        mocker.result(element_mock)

        element_mock['disabled']
        mocker.result(False)

        browser_mock.evaluate_script(script)
        mocker.result('null')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            is_enabled = driver.is_element_enabled(xpath)
            self.assertEqual(is_enabled, True)

    def test_going_back(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.back()
        browser_mock.evaluate_script('document.readyState')
        mocker.result( 'complete')

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.go_back()

    def test_is_element_visible_with_element_removal_while_executing(self):
        from selenium.common.exceptions import StaleElementReferenceException

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        xpath = '//div'

        browser_mock.find_by_xpath(xpath)

        element_mock = mocker.mock()
        mocker.result(element_mock)
        element_mock.visible
        mocker.throw(StaleElementReferenceException)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            is_visible = driver.is_element_visible(xpath)
            self.assertEqual(is_visible, False)

    def test_dialog_text(self):

        mocker = Mocker()

        text = 'Some text'
        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.get_alert()

        alert_mock = mocker.mock()
        mocker.result(alert_mock)
        alert_mock.text
        mocker.result(text)

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            result = driver.get_dialog_text()
            self.assertEqual(result, text)

    def test_accept_dialog(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.get_alert()

        alert_mock = mocker.mock()
        mocker.result(alert_mock)
        alert_mock.accept()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.accept_dialog()

    def test_accept_dialog(self):

        mocker = Mocker()

        context = Context(Settings())
        browser_mock = mocker.mock()

        browser_mock.get_alert()

        alert_mock = mocker.mock()
        mocker.result(alert_mock)
        alert_mock.dismiss()

        with mocker:
            driver = SplinterDriver(context, browser=browser_mock)
            driver.dismiss_dialog()
