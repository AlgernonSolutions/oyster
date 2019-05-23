import os
from datetime import datetime
from algernon import ajson

from toll_booth.obj.gql.gql_event_client import GqlClient
from toll_booth.obj.sapper.event_history import EventHistory, StateEvent


class Sapper:
    def __init__(self, state_gql_endpoint: str = None):
        if not state_gql_endpoint:
            state_gql_endpoint = os.environ['STATE_GQL_ENDPOINT']
        self._gql_client = GqlClient(state_gql_endpoint)

    def add_state_event(self, flow_id, run_id, state_type, state_timestamp, state_properties):
        return self._gql_client.add_state(flow_id, run_id, state_type, state_properties, state_timestamp)

    def retrieve_state_history(self, flow_id: str, run_id: str) -> EventHistory:
        events = self._gql_client.retrieve_flow_history(flow_id, run_id)
        return EventHistory([StateEvent(**x) for x in events])

    def mark_event_started(self, flow_id, run_id, task_name, task_kwargs):
        state_properties = [
            {
                'property_name': 'task_name',
                'property_value': task_name
            },
            {
                'property_name': 'task_kwargs',
                'property_value': ajson.dumps(task_kwargs)
            }
        ]
        state_timestamp = datetime.utcnow().timestamp()
        self.add_state_event(flow_id, run_id, 'EventStarted', state_timestamp, state_properties)

    def mark_event_completed(self, flow_id, run_id, task_name, task_kwargs, results):
        state_properties = [
            {
                'property_name': 'task_name',
                'property_value': task_name
            },
            {
                'property_name': 'task_kwargs',
                'property_value': ajson.dumps(task_kwargs)
            },
            {
                'property_name': 'task_results',
                'property_value': ajson.dumps(results)
            }
        ]
        state_timestamp = datetime.utcnow().timestamp()
        self.add_state_event(flow_id, run_id, 'EventCompleted', state_timestamp, state_properties)

    def mark_event_failed(self, flow_id, run_id, task_name, task_kwargs, failure_details):
        state_properties = [
            {
                'property_name': 'task_name',
                'property_value': task_name
            },
            {
                'property_name': 'task_kwargs',
                'property_value': ajson.dumps(task_kwargs)
            },
            {
                'property_name': 'failure_details',
                'property_value': ajson.dumps(failure_details)
            }
        ]
        state_timestamp = datetime.utcnow().timestamp()
        self.add_state_event(flow_id, run_id, 'EventFailed', state_timestamp, state_properties)
