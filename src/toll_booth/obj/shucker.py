import os

import boto3
from algernon import ajson

from toll_booth.obj.sapper.vinny import Sapper


class TaskManager:
    def __init__(self, run_id, flow_id, task_name, task_kwargs, sapper=None):
        if not sapper:
            sapper = Sapper()
        self._client = boto3.client('lambda')
        self._run_id = run_id
        self._flow_id = flow_id
        self._task_name = task_name
        self._task_kwargs = task_kwargs
        self._sapper = sapper

    @property
    def payload(self):
        return {
            'task_name': self._task_name,
            'run_id': self._run_id,
            'flow_id': self._flow_id,
            'task_kwargs': self._task_kwargs
        }

    def _fire_lambda(self):
        return self._client.invoke(
            FunctionName=os.getenv('TASK_FUNCTION_ARN', self._task_name),
            InvocationType='RequestResponse',
            Payload=ajson.dumps(self.payload)
        )

    def send_task(self):
        self._sapper.mark_event_started(**self.payload)
        try:
            response = self._fire_lambda()
            response_payload = response['Payload'].read()
            status_code = response['StatusCode']
            if status_code != 200:
                fn_error = response['FunctionError']
                log_results = response['LogResult']
                failure_details = {
                    'cause': fn_error,
                    'failure_logs': log_results,
                    'status_code': status_code,
                    'fn_response': response_payload
                }
                self._sapper.mark_event_failed(failure_details=failure_details, **self.payload)
                return
            result = ajson.loads(response_payload)
            self._sapper.mark_event_completed(results={'results': result}, **self.payload)
            return result
        except Exception as e:
            failure_details = ajson.dumps({'cause': e.args})
            self._sapper.mark_event_failed(failure_details=failure_details, **self.payload)
