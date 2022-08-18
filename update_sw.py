from os import access
import requests
import json
from urllib.error import HTTPError 

def makeRequest(method, session, url, data=None, exceptionMessage=None, handling=None):
    """makes a request and handles exceptions 

    Args:
        method (str): ['GET', 'POST', 'PATCH', 'DELETE'] request method
        session (requests.Session):
        url (str): url of the request
        data (dict, optional): data attached to the request. Defaults to None.
        exceptionMessage (str, optional): text added to the exception message. Defaults to None.
        handling (str, optional): [None, 'exit', 'raise']. what to do in case of exception, if None script moves on. Defaults to None.
    """
    headers = session.headers
    request = requests.Request(method=method, url=url, data=data, headers=headers)
    preped = request.prepare()

    try:
        response = session.send(preped)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        if handling == 'exit':
            SystemExit(exceptionMessage + '\n', errh)
        print(exceptionMessage + '\n', errh)
        if handling == 'raise':
            raise HTTPError

    return(response)

def software_update(machine_list, access_token, software_id, execType='WITHOUT_NOTIFICATION'):
    """updates software on a machine

    Args:
        machine_list (list): list of machine_id of the machines we want to update
        access_token (str): Bearer token with the write access for target machines
        software_id (str): software_id of the software we want to update
        execType (str): how to execute the update. ['WITHOUT_NOTIFICATION', 'WITH_NOTIFICATION']
        side (str, optional): ['LEFT', 'RIGHT', 'CENTER']. Defaults to 'LEFT'. 
    """

    if type(machine_list) == int:
        machine_list = [machine_list]
    else:
        machine_list = list(machine_list)
    update_session = requests.Session()
    update_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer '+access_token})

    for machine_id in machine_list:

        baseUrl = 'https://api.eversys-telemetry.com/v3/machines/'

        
        
        url = baseUrl + '{machine_id}/software-updates'.format(machine_id=machine_id)
        data = {'execType': execType, 'machineId': machine_id, 'softwareId': software_id}
        data = json.dumps(data, indent=4)
        exceptionMessage = 'Coud not update software on machine'
        updateRequest = makeRequest('POST', update_session, url, data=data, exceptionMessage=exceptionMessage, handling='exit')
        print(updateRequest.json())

