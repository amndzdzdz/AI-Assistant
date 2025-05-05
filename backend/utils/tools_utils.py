import json
from typing import Callable, List, Union

def get_fn_signature(fn: Callable):
    fn_signature = {
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": {
            "properties": {}
        }
    }

    schema = {k: {"type": v.__name__} for k, v in fn.__annotations__.items() if k != "return"}
    fn_signature["parameters"]["properties"] = schema
    return fn_signature


class Tool:
    def __init__(self, name: str, fn: Callable, fn_signature: str):
        self.name = name
        self.fn = fn
        self.fn_signature = fn_signature

    def __str__(self):
        return self.fn_signature
    
    def run(self, **kwargs):
        return self.fn(**kwargs)
    

def tool(fn: Callable):
    def wrapper():
        fn_signature = get_fn_signature(fn)
        return Tool(
            name=fn_signature.get("name"),
            fn=fn,
            fn_signature=json.dumps(fn_signature)
        )
    return wrapper()

def validate_arguments(tool_call: dict, tool_signature: dict) -> dict:
    """
    Validates and converts arguments in the input dictionary to match the expected types.

    Args:
        tool_call (dict): A dictionary containing the arguments passed to the tool.
        tool_signature (dict): The expected function signature and parameter types.

    Returns:
        dict: The tool call dictionary with the arguments converted to the correct types if necessary.
    """
    properties = tool_signature["parameters"]["properties"]

    # TODO: This is overly simplified but enough for simple Tools.
    type_mapping = {
        "int": int,
        "str": str,
        "bool": bool,
        "float": float,
    }

    for arg_name, arg_value in tool_call["arguments"].items():
        expected_type = properties[arg_name].get("type")

        if not isinstance(arg_value, type_mapping[expected_type]):
            tool_call["arguments"][arg_name] = type_mapping[expected_type](arg_value)

    return tool_call

def delete_appointment(appointment_ids: Union[str, List[str]], service):

    if isinstance(appointment_ids, str):
        service.events().delete(
            calendarId="primary",
            eventId=appointment_ids,
            sendNotifications=False
        ).execute()
        return "Appointment successfully deleted!"

    elif isinstance(appointment_ids, list):
        for appointment_id in appointment_ids:
            service.events().delete(
                calendarId="primary",
                eventId=appointment_id,
                sendNotifications=False
            ).execute()
        return "Appointments successfully deleted!"

    else:
        return "Invalid input type. Please provide a string or list of strings."

def create_appointment(appointment_name: str, 
                       appointment_description: str, 
                       appointment_start_date: str, 
                       appointment_end_date: str,
                       location: str,
                       service):
    event = {
        'summary': appointment_name,
        'description': appointment_description,
        'location': location,
        'start': {
            'dateTime': appointment_start_date
        },
        'end': {
            'dateTime': appointment_end_date
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    
    return f"Appointment created successfully! View it here: {created_event.get('htmlLink')}"

if __name__ == '__main__':
    def dummy_function(name: str, lname: str):
        """This is just a dummy function"""
        return name + " " + lname
    
    dummy_function_tool = tool(dummy_function)