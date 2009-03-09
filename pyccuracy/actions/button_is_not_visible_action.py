from pyccuracy.errors import *
from pyccuracy.actions.element_selector import *
from pyccuracy.actions.action_base import *
from pyccuracy.actions.element_is_visible_base import *

class ButtonIsNotVisibleAction(ElementIsVisibleBase):
    def __init__(self, browser_driver, language):
        super(ButtonIsNotVisibleAction, self).__init__(browser_driver, language)

    def get_selector(self, element_name):
        return ElementSelector.button(element_name)

    def matches(self, line):
        reg = self.language["button_is_not_visible_regex"]
        self.last_match = reg.search(line)
        return self.last_match

    def values_for(self, line):
        return self.last_match and (self.last_match.groups()[1],) or tuple([])

    def execute(self, values, context):
        button_name = values[0]
        error_message = self.language["button_is_not_visible_failure"]
        self.execute_is_not_visible(button_name, error_message)