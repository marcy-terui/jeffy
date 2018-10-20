from logging import Logger

from jeffy import framework

from mock import Mock

import pytest


def test_setup():
    assert isinstance(
        framework.setup(
            logger=Logger('test'),
            enable_event_logging=True,
            enable_result_logging=True
            ),
        framework.Jeffy)


class TestJeffy(object):

    def setup_method(self, method):
        self.jeffy = framework.Jeffy(
            logger=Logger('test'),
            enable_event_logging=True,
            enable_result_logging=True)

    def test_jeffy_log(self):
        self.jeffy.log('foo')

    def test_general_event_handler(self):
        func = self.jeffy.general_event_handler(Mock(return_value='foo'))
        assert func({}, {}) == 'foo'

    def test_stepf_exception(self):
        func = self.jeffy.general_event_handler(Mock(side_effect=Exception('foo')))
        with pytest.raises(Exception):
            func({}, {})
