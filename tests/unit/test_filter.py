import pytest
from algernon import ajson

from toll_booth.tasks import handler


@pytest.mark.filter
class TestFilter:
    def test_event_filter_open_history(self,
                                       task_manager_mock,
                                       sapper_mock,
                                       called_event,
                                       open_event_history,
                                       mock_context):
        mock_sapper_obj = sapper_mock(open_event_history)
        mock_sapper = mock_sapper_obj.return_value
        mock_task_manager = task_manager_mock()
        results = handler(called_event, mock_context)
        for entry in called_event['Records']:
            body = ajson.loads(entry['body'])
            event = ajson.loads(body['Message'])
            mock_task_manager.assert_not_called()
            mock_sapper.retrieve_state_history.assert_called_with(event['flow_id'], event['run_id'])
        assert results

    def test_event_filter_timed_out_history(self,
                                            task_manager_mock,
                                            sapper_mock,
                                            called_event,
                                            timed_out_event_history,
                                            mock_context):
        mock_sapper_obj = sapper_mock(timed_out_event_history)
        mock_sapper = mock_sapper_obj.return_value
        mock_task_manager = task_manager_mock()
        results = handler(called_event, mock_context)
        for entry in called_event['Records']:
            body = ajson.loads(entry['body'])
            event = ajson.loads(body['Message'])
            mock_sapper.retrieve_state_history.assert_called_with(event['flow_id'], event['run_id'])
            mock_sapper.mark_event_failed.assert_called_with(failure_details={'cause': 'timed_out'}, **event)
            mock_sapper.mark_event_started.assert_called_with(**event)
            mock_task_manager.assert_called()
            mock_sapper.mark_event_completed.assert_called_with(results={'results': {'some_result': 'here'}}, **event)
        assert results

    def test_event_filter_failed_history(self,
                                         task_manager_mock,
                                         sapper_mock,
                                         called_event,
                                         failed_event_history,
                                         mock_context):
        mock_sapper_obj = sapper_mock(failed_event_history)
        mock_sapper = mock_sapper_obj.return_value
        mock_task_manager = task_manager_mock()
        results = handler(called_event, mock_context)
        for entry in called_event['Records']:
            body = ajson.loads(entry['body'])
            event = ajson.loads(body['Message'])
            mock_sapper.retrieve_state_history.assert_called_with(event['flow_id'], event['run_id'])
            mock_sapper.mark_event_failed.assert_not_called()
            mock_sapper.mark_event_started.assert_called_with(**event)
            mock_task_manager.assert_called()
            mock_sapper.mark_event_completed.assert_called_with(results={'results': {'some_result': 'here'}}, **event)
        assert results
