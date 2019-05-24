import json
from os import path
from unittest.mock import patch, MagicMock, create_autospec
from algernon import ajson

import pytest

from tests.event_generator import StateEventGenerator


@pytest.fixture
def task_manager_mock():
    patches = []

    def _generate_task_manager(**kwargs):

        payload_mock = MagicMock(name='payload')
        payload_mock.read.return_value = ajson.dumps(kwargs.get('payload', {'some_result': 'here'}))
        response = {
            'Payload': payload_mock,
            'StatusCode': kwargs.get('status_code', 200)
        }
        if kwargs.get('function_error'):
            response['FunctionError'] = kwargs.get('function_error')
        if kwargs.get('log_result'):
            response['LogResult'] = kwargs.get('log_result')
        retrieve_patch_obj = patch('toll_booth.obj.shucker.TaskManager._fire_lambda')
        patches.append(retrieve_patch_obj)
        mock_obj = retrieve_patch_obj.start()
        mock_obj.return_value = response
        return mock_obj

    yield _generate_task_manager
    for entry in patches:
        entry.stop()


@pytest.fixture
def sapper_mock():
    patches = []

    def _generate_sapper(history_items):
        from toll_booth.obj.sapper.event_history import EventHistory, StateEvent
        from toll_booth.obj.sapper.vinny import Sapper
        retrieve_patch_obj = patch('toll_booth.tasks.Sapper')
        patches.append(retrieve_patch_obj)
        mock_obj = retrieve_patch_obj.start()
        test_history = EventHistory([StateEvent(**x) for x in history_items])
        mock_sapper = create_autospec(Sapper)
        mock_history = MagicMock(return_value=test_history)
        mock_sapper.retrieve_state_history = mock_history
        mock_obj.return_value = mock_sapper
        return mock_obj

    yield _generate_sapper
    for entry in patches:
        entry.stop()


@pytest.fixture
def called_event():
    event = _read_test_event('called_event')
    return _generate_queued_event(event)


@pytest.fixture
def open_event_history():
    history = [StateEventGenerator().state_event]
    return history


@pytest.fixture
def timed_out_event_history():
    history = [StateEventGenerator(is_timed_out=True).state_event]
    return history


@pytest.fixture
def completed_event_history():
    history = [
        StateEventGenerator().state_event,
        StateEventGenerator(state_type='EventFailed').state_event,
        StateEventGenerator().state_event,
        StateEventGenerator(state_type='EventCompleted').state_event,
    ]
    return history


@pytest.fixture
def failed_event_history():
    history = [
        StateEventGenerator().state_event,
        StateEventGenerator(state_type='EventFailed').state_event
    ]
    return history


@pytest.fixture(autouse=True)
def silence_x_ray():
    x_ray_patch_all = 'algernon.aws.lambda_logging.patch_all'
    patch(x_ray_patch_all).start()
    yield
    patch.stopall()


@pytest.fixture
def mock_context():
    from unittest.mock import MagicMock
    context = MagicMock(name='context')
    context.__reduce__ = cheap_mock
    context.function_name = 'test_function'
    context.invoked_function_arn = 'test_function_arn'
    context.aws_request_id = '12344_request_id'
    context.get_remaining_time_in_millis.side_effect = [1000001, 500001, 250000, 0]
    return context


def cheap_mock(*args):
    from unittest.mock import Mock
    return Mock, ()


def _read_test_event(event_name):
    with open(path.join('tests', 'test_events', f'{event_name}.json')) as json_file:
        event = json.load(json_file)
        return event


def _generate_queued_event(event):
    event_string = ajson.dumps(event)
    message_object = {'Message': event_string}
    body_object = {'body': ajson.dumps(message_object)}
    return {'Records': [body_object]}
