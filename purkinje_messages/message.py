# -*- coding: utf-8 -*-

"""Message/event type for communication with browser and test runner"""
from builtins import object

from datetime import datetime
from copy import deepcopy
import json
import abc
from future.utils import with_metaclass
from voluptuous import Schema, Required
import logging

logger = logging.getLogger(__name__)


# Registry of all known event types
EVENT_REGISTRY = {}


class MessageException(Exception):

    """Message-related error
    """
    pass


class MsgType(object):

    """Constants for messages"""
    TERMINATE_CONNECTION = 'terminate_connection'

    # Meta information about project under test
    PROJ_INFO = 'proj_info'

    TESTSUITE_STARTED = 'testsuite_started'
    TC_STARTED = 'tc_started'
    TC_FINISHED = 'tc_finished'

    # Premature abort
    ABORTED = 'aborted'

    # aborted due to an error
    ERROR = 'error'


class Event(with_metaclass(abc.ABCMeta, object)):

    """An event for the browser"""

    def __init__(self, schema, **kwargs):
        """ :param schema: a voluptuous schema containing additional
                           constraints. Constraints are merged with
                           the base class constraints
        """
        self.timestamp = datetime.now()
        self.data = {'type': kwargs['type'],
                     'text': kwargs['text'],
                     'timestamp': datetime.isoformat(
                         self.timestamp)}

        base_schema = {
            Required('type'): str,
            Required('timestamp'): str,
            Required('text'): str
        }
        schema = deepcopy(schema)
        schema.update(base_schema)
        self._schema = Schema(schema)

    def validate(self):
        """Schema validation of message contents
        """
        self._schema(self.data)

    def serialize(self):
        """Creates JSON representation of Event object.
           Triggers a validation
        """
        self.validate()
        self._serialize(self.data)
        return json.dumps(self.data)

    def __getitem__(self, key):
        """Access to message content dictionary
        """
        return self.data[key]

    @abc.abstractmethod
    def _serialize(self, body):
        """payload, to be filled with message type specific data """

    def __unicode__(self):
        return u'{}: [{}] {}'.format(self.data['type'],
                                     self.data['timestamp'],
                                     self.data['text'])

    @staticmethod
    def parse(event_json):
        """Creates an appropriate event object from JSON representation
        """
        event_dict = json.loads(event_json)
        event_type = event_dict.get('type')
        if not event_type:
            raise MessageException('Missing event type')
        event_cls = EVENT_REGISTRY.get(event_type)
        if not event_cls:
            raise MessageException('Unknown event type {}'.format(event_type))
        return event_cls(**event_dict)


def register_eventclass(event_id):
    """Decorator for registering event classes for parsing
    """
    def register(cls):
        EVENT_REGISTRY[event_id] = cls
        logger.debug('######### Event registry is now: {}'.format(
            EVENT_REGISTRY))
        return cls
    return register


@register_eventclass(MsgType.TC_STARTED)
class TestCaseStartEvent(Event):

    def __init__(self, **kwargs):
        schema = {}
        kwargs['type'] = MsgType.TC_STARTED
        super(TestCaseStartEvent, self).__init__(schema,
                                                 **kwargs)

    def _serialize(self, body):
        pass  # no extra data


@register_eventclass(MsgType.TERMINATE_CONNECTION)
class ConnectionTerminationEvent(Event):

    def __init__(self, **kwargs):
        schema = {}
        super(ConnectionTerminationEvent, self).__init__(
            schema,
            type=MsgType.TERMINATE_CONNECTION,
            text='')

    def _serialize(self, body):
        pass
