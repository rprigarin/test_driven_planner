"""Set up MongoDB access and manage queries related to planner tasks."""

import pymongo

# ________________________________________________________________________________

def validate_task_query_fields(task_query):
    fields = list(task_query.keys())

    if len(fields) < 2:
        return False
    
    return True if fields[0]=='date' and fields[1]=='task_desc' else False