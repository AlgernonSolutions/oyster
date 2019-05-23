from algernon.aws.gql import GqlNotary
from algernon import ajson

from toll_booth.obj.gql import gql_queries


class GqlClient:
    def __init__(self, gql_endpoint):
        self._gql_endpoint = gql_endpoint
        self._connection = GqlNotary(gql_endpoint)

    def _send_command(self, command, variables=None):
        if not variables:
            variables = {}
        return ajson.loads(self._connection.send(command, variables))

    def add_state(self, flow_id, run_id, state_type, state_properties, state_timestamp):
        command = gql_queries.ADD_STATE
        variables = {
          "input": {
            "flow_run_id": f"{flow_id}#{run_id}",
            "state_type": state_type,
            "state_timestamp": state_timestamp,
            "state_properties": state_properties
          }
        }
        return self._send_command(command, variables)

    def _retrieve_flow_history(self, flow_id, run_id, token=None):
        query = gql_queries.RETRIEVE_HISTORY
        variables = {
            'flow_run_id': f'{flow_id}#{run_id}'
        }
        if token:
            variables['nextToken'] = token
        response = self._send_command(query, variables)
        results = response['data']['listStateEntries']
        history = [x for x in results['items']]
        token = results['nextToken']
        return history, token

    def retrieve_flow_history(self, flow_id, run_id):
        flow_history = []
        history_items, token = self._retrieve_flow_history(flow_id, run_id)
        flow_history.extend(history_items)
        while token is not None:
            history_items, token = self._retrieve_flow_history(flow_id, run_id, token)
            flow_history.extend(history_items)
        return flow_history
