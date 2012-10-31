#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Bernardo Heynemann <heynemann@gmail.com>
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
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

from re import compile as re_compile

from mocker import Mocker

from pyccuracy import Page
from pyccuracy.common import Settings
from pyccuracy.errors import ActionFailedError
from pyccuracy.actions.core.page_actions import *

from ..utils import assert_raises, Object

class FakeContext(object):
    def __init__(self, mocker):
        self.settings = Settings(cur_dir='/')
        self.browser_driver = mocker.mock()
        self.language = mocker.mock()
        self.current_page = None

#Go To Action

def test_page_go_to_action_calls_the_right_browser_driver_methods():

    mocker = Mocker()

    context = FakeContext(mocker)

    context.browser_driver.page_open("file:///some_url")
    context.browser_driver.wait_for_page()

    with mocker:
        action = PageGoToAction()

        action.execute(context, url='"some_url"')

def test_page_go_to_action_sets_context_current_url():
    mocker = Mocker()

    context = FakeContext(mocker)

    context.browser_driver.page_open("file:///some_url")
    context.browser_driver.wait_for_page()

    with mocker:
        action = PageGoToAction()

        action.execute(context, url='"some_url"')

    assert context.url == "file:///some_url"

def test_page_go_to_action_sets_page_if_page_is_supplied():
    class SomePage(Page):
        url = "some"

    mocker = Mocker()

    context = FakeContext(mocker)

    context.browser_driver.page_open("file:///some")
    context.browser_driver.wait_for_page()

    with mocker:
        action = PageGoToAction()

        action.execute(context, url="Some Page")

    assert isinstance(context.current_page, SomePage)

def test_page_go_to_action_raises_with_invalid_page():

    mocker = Mocker()

    context = FakeContext(mocker)

    context.language.format("page_go_to_failure", "http://www.google.com")
    mocker.result("Error Message")

    with mocker:
        action = PageGoToAction()
        assert_raises(ActionFailedError, action.execute, context=context, url="http://www.google.com",
                      exc_pattern=re_compile(r'^Error Message$'))

#End Go To Action

#Go To With Parameters Action

def test_page_go_to_with_parameters_action_raises_error_when_parameters_are_invalid():

    mocker = Mocker()

    action = PageGoToWithParametersAction()

    context = FakeContext(mocker)

    context.language.format('page_go_to_with_parameters_failure', 'Blah blahabla blah')
    mocker.result('Error Message')

    with mocker:

        assert_raises(ActionFailedError, action.parse_parameters, context, 'Blah blahabla blah')

def test_page_go_to_with_parameters_action_parses_parameters():

    mocker = Mocker()

    action = PageGoToWithParametersAction()

    context = FakeContext(mocker)

    with mocker:
        params = action.parse_parameters(context, 'parameter1 "value1"')
        assert params == { 'parameter1':'value1' }

        params = action.parse_parameters(context, 'query_string "?another+value=x%20y%20z"')
        assert params == { 'query_string':'?another+value=x%20y%20z' }

def test_page_go_to_with_parameters_action_parses_many_parameters():

    mocker = Mocker()

    action = PageGoToWithParametersAction()

    context = FakeContext(mocker)

    with mocker:
        params = action.parse_parameters(context, 'parameter1 "value1", parameter2 "value2"')
        assert params == { 'parameter1':'value1', 'parameter2':'value2' }

        params = action.parse_parameters(context, 'query_string "?another+value=x%20y%20z", user "gchapiewski"')
        assert params == { 'query_string':'?another+value=x%20y%20z', 'user':'gchapiewski' }

        params = action.parse_parameters(context, 'parameter1 "value1", parameter2 "value2", param3 "value3"')
        assert params == { 'parameter1':'value1', 'parameter2':'value2', 'param3':'value3' }

def test_page_go_to_with_parameters_action_resolves_url_for_parameter():
    action = PageGoToWithParametersAction()
    url = '/user/<username>'
    params = {'username':'gchapiewski'}
    assert action.replace_url_paremeters(url, params) == '/user/gchapiewski'

def test_page_go_to_with_parameters_action_resolves_url_for_many_parameters():
    action = PageGoToWithParametersAction()
    url = '/search.php?q=<query>&order=<order>&p=<page>'
    params = {'query':'xpto', 'order':'desc', 'page':'10' }
    assert action.replace_url_paremeters(url, params) == '/search.php?q=xpto&order=desc&p=10'

#End Go To With Parameters Action

#Am In Action

def test_page_am_in_action_calls_the_right_browser_driver_methods():

    mocker = Mocker()

    class SomePage(Page):
        url = "http://www.somepage.com"

    context = FakeContext(mocker)

    with mocker:
        action = PageAmInAction()

        action.execute(context, url="http://www.somepage.com")
        assert isinstance(context.current_page, SomePage)
        assert context.url == "http://www.somepage.com"

def test_page_am_in_action_sets_page_if_page_is_supplied():

    mocker = Mocker()

    class SomePage1(Page):
        url = "http://www.somepage.com"

    context = FakeContext(mocker)

    with mocker:
        action = PageAmInAction()

        action.execute(context, url="Some Page 1")
        assert isinstance(context.current_page, SomePage1)
        assert context.url == "http://www.somepage.com"

def test_page_am_in_action_raises_if_no_page():

    mocker = Mocker()

    context = FakeContext(mocker)

    context.language.format("page_am_in_failure", "http://www.google.com")
    mocker.result("Error Message")

    with mocker:
        action = PageAmInAction()

        assert_raises(ActionFailedError, action.execute, context=context, url="http://www.google.com",
                      exc_pattern=re_compile(r'^Error Message$'))

#End Am In Action

# Page See Title Action

def test_page_see_title_action_calls_the_right_browser_driver_methods():

    mocker = Mocker()

    context = FakeContext(mocker)

    context.browser_driver.get_title()
    mocker.result("some title")

    with mocker:

        action = PageSeeTitleAction()

        action.execute(context, title="some title")

#End Page See Title Action

#Page Refresh Action

def test_page_refresh_action_calls_the_right_browser_driver_methods():

    mocker = Mocker()

    context = FakeContext(mocker)

    context.browser_driver.refresh()

    with mocker:

        action = PageRefreshAction()

        action.execute(context)

#End Page Refresh Action
