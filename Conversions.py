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
            fields_by_name = {field['name']: field for field in json.get("fields", [])}
        except:
            fields_by_name = {}

        self.status = self._get_fields_(fields_by_name, ["Status", 'value', 'name', 'raw'], "Não planejado ainda")
        self.assignee = self._get_fields_(fields_by_name, ["Assignees", 'value', 0,'login'])
        self.labels = self._get_fields_(fields_by_name, ["Labels", 'value', 0, 'name'])
        self.priority = self._get_fields_(fields_by_name, ["Priority", 'value', 'name', 'raw'])
        self.estimate = self._get_fields_(fields_by_name, ["Estimate", 'value'])

        # Para os campos de data, podemos adicionar a conversão
        start_date_str = self._get_fields_(fields_by_name, ["Start date", 'value'])
        self.start_date = convertJsonToDate(start_date_str) if start_date_str else None

        end_date_str = self._get_fields_(fields_by_name, ["End date", 'value'])
        self.end_date = convertJsonToDate(end_date_str) if end_date_str else None

        # O campo 'closed_at' parece estar fora de 'fields', então o buscamos diretamente
        closed_at_str = self._get_fields_(json, ["content", 'closed_at'])
        self.closed_at = convertJsonToDate(closed_at_str) if closed_at_str else None

  
    def _get_fields_(self, data_dict, path, default = None):
        current_level = data_dict
        for key in path:
            try:
                current_level = current_level[key]
            except:
                return default
        return current_level

def convertJsonToDate(value: str) -> datetime.datetime | None:
    formatString = '%Y-%m-%dT%H:%M:%S%z'
    if not value:
        return None
    try:
        # Formato que corresponde a "2025-08-01T00:00:00+00:00"
        formatString = '%Y-%m-%dT%H:%M:%S%z'
        # O datetime.fromisoformat lida com isso de forma mais elegante (veja Solução 2)
        return datetime.datetime.strptime(value, formatString)
    except (ValueError, TypeError):
        return None


def getDateString(value: datetime.datetime):
    return f"{value.date}/{value.month}/{value.year}"


def get_project_items_by_json(json) -> list[RequestProjectItemsResponse]:
    list = []
    for issue in json:
        list.append(RequestProjectItemsResponse(issue))
    return list
