from datetime import datetime
from typing import List


class StateEvent:
    def __init__(self, state_type, state_timestamp, flow_run_id, state_id, state_properties):
        self._state_type = state_type
        self._state_timestamp = state_timestamp
        self._flow_run_id = flow_run_id
        self._state_id = state_id
        self._state_properties = state_properties

    @property
    def state_type(self):
        return self._state_type

    @property
    def state_timestamp(self):
        return self._state_timestamp

    @property
    def flow__run_id(self):
        return self._flow_run_id

    @property
    def state_properties(self):
        return self._state_properties

    @property
    def is_start(self):
        return self._state_type == 'EventStarted'

    @property
    def is_fail(self):
        return self._state_type == 'EventFailed'

    @property
    def is_complete(self):
        return self._state_type == 'EventCompleted'

    def __getitem__(self, item):
        for event_property in self._state_properties:
            property_name = event_property['property_name']
            if property_name == item:
                return event_property['property_value']
        raise KeyError(item)


class EventHistory:
    def __init__(self, events: List[StateEvent] = None):
        if not events:
            events = []
        self._events = events

    @property
    def events(self):
        return self._events

    @property
    def start_events(self):
        return [x for x in self._events if x.is_start]

    @property
    def complete_events(self):
        return [x for x in self._events if x.is_complete]

    @property
    def fail_events(self):
        return [x for x in self._events if x.is_fail]

    @property
    def end_events(self):
        end_events = []
        end_events.extend(self.fail_events)
        end_events.extend(self.complete_events)
        return end_events

    @property
    def is_started(self):
        if self.start_events:
            return True
        return False

    @property
    def is_completed(self):
        if self.complete_events:
            return True
        return False

    @property
    def is_open(self):
        return len(self.start_events) > len(self.end_events)

    @property
    def is_failed(self):
        if self.is_completed:
            return False
        return len(self.start_events) == len(self.fail_events)

    @property
    def is_timed_out(self):
        if not self.is_started:
            return False
        if self.is_completed:
            return False
        if self.is_failed:
            return False
        ordered_events = sorted(self.start_events, key=lambda x: x.state_timestamp, reverse=True)
        for event in ordered_events:
            start_timestamp = event.state_timestamp
            start_datetime = datetime.fromtimestamp(float(start_timestamp))
            now = datetime.utcnow()
            run_time = (now - start_datetime).total_seconds()
            max_run_time = 15*60
            if run_time > max_run_time:
                return True
        return False

    @property
    def task_results(self):
        if not self.is_completed:
            raise RuntimeError(f'attempted to retrieve the results of an event_history before it is completed')
        complete_events = [x for x in self._events if x.is_complete]
        results = {([x['task_results'] for x in complete_events])}
        if len(results) > 1:
            raise RuntimeError(f'an event_history produced multiple differing results, not sure how to proceed')
        for result in results:
            return result

    def __iter__(self):
        return iter(self._events)
