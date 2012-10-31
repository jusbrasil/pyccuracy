#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

from pyccuracy.actions import ActionBase
from pyccuracy.languages import LanguageItem

class ConfirmDialogAction(ActionBase):
    '''h3. Example

  * And I expect a dialog with "Continue?" and confirm

h3. Description

This action asserts that a dialog as the given message and confirm it.'''
    __builtin__ = True
    regex = LanguageItem("dialog_has_text_and_confirm_regex")

    def execute(self, context, message):

        current_message = context.browser_driver.get_dialog_text()
        if (message != current_message):
            context.browser_driver.dismiss_dialog()
            error_message = context.language.format("dialog_has_text_failure", message, current_message)
            raise self.failed(error_message)
        context.browser_driver.accept_dialog()
