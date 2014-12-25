# -*- coding: utf-8 -*-

"""Test cases for messages"""
from __future__ import absolute_import
from builtins import str
import json
import sys
import pytest
from datetime import datetime
from mock import Mock
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

import purkinje_messages.message as sut


@pytest.fixture
def mock_date(monkeypatch):
    m = Mock()
    m.now.return_value = datetime(2014, 2, 1, 8, 9, 10)
    monkeypatch.setattr(sut,
                        'datetime',
                        m)
    m.isoformat = datetime.isoformat


@pytest.fixture
def tc_start_event(mock_date):
    return sut.TestCaseStartEvent(text='mytext')


@pytest.fixture
def connection_termination_event(mock_date):
    return sut.ConnectionTerminationEvent()


def test_tc_start_event_unicode(tc_start_event):
    assert str(
        tc_start_event) == 'tc_started: [2014-02-01T08:09:10] mytext'


def test_connection_termination_unicode(connection_termination_event):
    expected = ('terminate_connection: '
                '[2014-02-01T08:09:10] ')
    assert str(connection_termination_event) == expected


# @pytest.skip('needs mock')
#  def test_timestamp(tc_start_event):
#     assert isinstance(tc_start_event.timestamp, datetime)


def test_tc_start_event_serialize(tc_start_event):
    serialized = tc_start_event.serialize()
    expected = json.dumps({'text': 'mytext',
                           'type': 'tc_started',
                           'timestamp': '2014-02-01T08:09:10'
                           })
    assert serialized == expected
    print serialized


def test_connection_termination_serialize(connection_termination_event):
    serialized = connection_termination_event.serialize()
    expected = json.dumps({'text': '',
                           'type': 'terminate_connection',
                           'timestamp': '2014-02-01T08:09:10'
                           })
    assert serialized == expected


def test_parse_tc_start():
    event_json = ('{"text": "mytext", "type": "tc_started",'
                  ' "timestamp": "2014-02-01T08:09:10"}')
    sut.Event.parse(event_json)


def test_parse_connection_termination():
    event_json = ('{"text": "", "type": "terminate_connection",'
                  ' "timestamp": "2014-02-01T08:09:10"}')
    sut.Event.parse(event_json)


def test_getitem(tc_start_event):
    assert tc_start_event['timestamp'] \
        == '2014-02-01T08:09:10'


def test_register_eventclass():
    assert sut.MsgType.TC_STARTED in sut.EVENT_REGISTRY


def test_register_eventclass_2():
    dummy_event_id = 12345

    @sut.register_eventclass(dummy_event_id)
    class MyEvent(sut.Event):

        def __init__(self):
            schema = {}
            super(MyEvent, self).__init__(schema,
                                          type='dummy_type')
    assert dummy_event_id in sut.EVENT_REGISTRY
    assert sut.EVENT_REGISTRY[dummy_event_id] == MyEvent
