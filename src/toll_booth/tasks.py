import logging
from typing import Dict, Any

from algernon import queued, ajson
from algernon.aws import lambda_logged

from toll_booth.obj.sapper.vinny import Sapper
from toll_booth.obj.shucker import TaskManager


class InvalidEventException(Exception):
    def __init__(self, expected_keys, payload):
        msg = f'unable to process payload: {payload}, does not match expected keys: {expected_keys}'
        super().__init__(msg)


def _check_payload(payload: Dict[str, Any]):
    expected_keys = ['task_name', 'task_kwargs', 'flow_id', 'run_id']
    for payload_name in payload:
        if payload_name not in expected_keys:
            raise InvalidEventException(expected_keys, payload)
    for key_value in expected_keys:
        if key_value not in payload:
            raise InvalidEventException(expected_keys, payload)
    return True


@lambda_logged
@queued
def handler(event, context):
    logging.info(f'received a call to filter with the oyster, event: {event}, context: {context}')
    _check_payload(event)
    sapper = Sapper(event.get('state_gql_endpoint'))
    flow_id, run_id = event['flow_id'], event['run_id']
    history = sapper.retrieve_state_history(flow_id, run_id)
    if history.is_completed:
        logging.info(f'completed a call to the oyster, event: {event}, task is completed, not fired')
        return
    if history.is_open:
        if not history.is_timed_out:
            logging.info(f'completed a call to the oyster, event: {event}, task is open and not timed out, not fired')
            return
        if history.is_timed_out:
            logging.info(f'task: {event}, has timed out, fire again')
            sapper.mark_event_failed(failure_details={'cause': 'timed_out'}, **event)
    if history.is_failed:
        logging.info(f'task: {event} has failed, fire again')
    task_manager = TaskManager(sapper=sapper, **event)
    results = task_manager.send_task()
    logging.info(f'completed a call to filter with the oyster, event: {event}, context: {context}, results: {results}')
    return ajson.dumps(results)
