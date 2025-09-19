from re import split
import requests

import Conversions
import _secrets as s

def get_project_items(project_number: int, token: str) -> list[Conversions.RequestProjectItemsResponse]:
    uri = f"{s.GITHUB_API}/orgs/{s.ORGANIZATION}/projectsV2/{project_number}/items?"
    uri += "fields[]=206751654&" # Title  
    uri += "fields[]=206751655&" # assignees
    uri += "fields[]=206751656&" # status
    uri += "fields[]=206751657&" # labels
    uri += "fields[]=206751744&" # priority
    uri += "fields[]=206751746&" # estimate
    uri += "fields[]=206751748&" # start date
    uri += "fields[]=206751749" # end date
    uri += "&per_page=30"

    data, response = get(uri, token)

    hasLink = False
    try:
        _ = response.headers['link']
        hasLink = True
    except:
        return data

    if hasLink:
        afterValue, hasNext = verifyNext(response.headers['link'])
        while hasNext:
            newUri = uri + f"&after={afterValue}"
            
            newValues, response = get(newUri, token)
            data += newValues
            value, nxt = verifyNext(response.headers['link'])

            afterValue = value
            hasNext = nxt

    return data


def get(uri, token):

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-Github-Api-Version": "2022-11-28"
    }

    response = requests.get(uri, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Erro ao solicitar items do projeto\n {response.text}")
    
    data = Conversions.get_project_items_by_json(response.json())
    return data, response


def verifyNext(json: str) -> tuple[str, bool]:
    links = json.split(',')
    for link in links:
        link = link.split(';')
        hasNext = link[1].split('"')[1].lower() == 'next'
        if(not hasNext):
            continue
        after = link[0].split('after=')[1].replace('>','')
        if '&' in after:
            after = after.split("&")[0]
        return after, hasNext
    
    return "", False

