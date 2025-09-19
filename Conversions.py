import datetime

class RequestDeviceResponse:
    def __init__(self, json):
        self.device_code = json["device_code"]
        self.user_code = json["user_code"]
        self.verification_uri = json["verification_uri"]
        self.interval = json["interval"]
        self.expires_in = json["expires_in"]

class RequestTokenReponse:
    def __init__(self, json):
        self.successfull = True
        try:
            _ = json["access_token"]
        except:
            self.successfull = False
        
        if(not self.successfull):
            self.error = json["error"]
            self.error_description = json["error_description"]
            self.error_uri = json["error_uri"]
        else:
            self.access_token = json["access_token"]
            self.scope = json["scope"]
            self.token_type = json["token_type"]


class RequestProjectItemsResponse:
    def __init__(self, json):

        self.number = json["content"]['number']
        self.title = json["content"]['title']
        try:
            self.status = json["fields"][2]['value']['name']['raw']
        except:
            self.status = "Não planejado ainda"

        try:
            self.assignee = json["fields"][1]['value']['login']
        except :
            self.assignee = None
        try:
            self.labels = json["fields"][3]['values'][0]['name']
        except :
            self.labels = None

        try:
            self.priority = json["fields"][4]['value']['name']['raw']
        except :
            self.priority = None

        try:
            self.estimate = json["fields"][5]['value']
        except :
            self.estimate = None

        try:
            jsonDate:str = json["fields"][6]['value']
            self.start_date = convertJsonToDate(jsonDate)
        except :
            self.start_date = None

        try:
            jsonDate = json["fields"][7]['value']
            self.end_date = convertJsonToDate(jsonDate)
        except :
            self.end_date = None
        try:
            jsonDate = json["content"]['closed_at']
            self.closed_at = convertJsonToDate(jsonDate)
        except :
            self.closed_at = None
    

def convertJsonToDate(value: str) -> datetime.datetime:
    formatString = ""
    res = datetime.datetime.strptime(value, formatString)
    return res

def getDateString(value: datetime.datetime):
    return f"{value.date}/{value.month}/{value.year}"


def get_project_items_by_json(json) -> list[RequestProjectItemsResponse]:
    list = []
    for issue in json:
        list.append(RequestProjectItemsResponse(issue))
    return list
