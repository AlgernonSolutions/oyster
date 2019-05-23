ADD_STATE = '''
mutation AddState($input: CreateStateEntryInput!) {
    createStateEntry(input: $input){
        flow_run_id
        state_id
        state_properties{
            property_name
            property_value
        }
        state_type
    }
} 
'''

RETRIEVE_HISTORY = '''
query RetrieveHistory($flow_run_id: String!, $token: String){
  listStateEntries(filter: {flow_run_id: {eq: $flow_run_id}}, nextToken: $token){
    items{
      flow_run_id
      state_id
      state_type
      state_timestamp
      state_properties{
        property_name
        property_value
      }
    }
    nextToken
  }
}

'''