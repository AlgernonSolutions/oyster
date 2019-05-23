import uuid
from datetime import datetime, timedelta

from algernon import ajson


class StateEventGenerator:
    def __init__(self, **kwargs):
        self._task_name = kwargs.get('task_name', 'test_task')
        self._flow_id = kwargs.get('flow_id', 'some_test_flow')
        self._run_id = kwargs.get('run_id', '1001')
        self._task_kwargs = kwargs.get('task_kwargs', {'id_source', 'Algernon'})
        timestamp = datetime.utcnow()
        if kwargs.get('is_timed_out', False):
            timestamp = timestamp - timedelta(minutes=20)
        self._timestamp = timestamp.timestamp()
        self._state_type = kwargs.get('state_type', 'EventStarted')
        self._results = kwargs.get('results', {'some_results': 'go_here'})
        self._fail_details = kwargs.get('fail_details', {'cause': 'some failure reason'})

    @property
    def state_event(self):
        state_event = {
            "flow_run_id": f"{self._flow_id}#{self._run_id}",
            "state_id": uuid.uuid4().hex,
            "state_type": self._state_type,
            "state_timestamp": self._timestamp,
            "state_properties": [
                {
                    "property_name": "task_name",
                    "property_value": self._task_name
                },
                {
                    "property_name": "task_kwargs",
                    "property_value": ajson.dumps(self._task_kwargs)
                }
            ]
        }
        if self._state_type == 'EventCompleted':
            state_event['state_properties'].append({
                "property_name": "task_results",
                "property_value": ajson.dumps(self._results)
            })
        if self._state_type == 'EventFailed':
            state_event['state_properties'].append({
                "property_name": "fail_details",
                "property_value": ajson.dumps(self._fail_details)
            })
        return state_event
