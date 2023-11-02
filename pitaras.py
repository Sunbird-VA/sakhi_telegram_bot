import requests
import json

def make_post_api_request(url, headers, data):
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()

def make_get_api_request(url, headers, data):
    response = requests.get(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()


def find_children_with_mime_type(content):
    coontentMetdata = []
    for child in content["children"]:
        if child["mimeType"] in ["application/pdf", "video/mp4"]:
            coontentMetdata.append({ 
                "name": child["name"],
                "previewUrl": child["previewUrl"],
                "artifactUrl": child["artifactUrl"],
                # "streamingUrl": child["streamingUrl"],
                "downloadUrl": child["downloadUrl"],
                "mimeType": child["mimeType"],
                "identifier" : child["identifier"],
                "contentType": child["contentType"]
            })
        elif child["mimeType"] == "application/vnd.ekstep.content-collection":
            coontentMetdata.extend(find_children_with_mime_type(child))
    return coontentMetdata

def get_metadata_of_children(identifier):
    url = "https://sunbirdsaas.com/action/content/v3/hierarchy/{}".format(identifier)
    response = make_get_api_request(url, None, None)
    contents = find_children_with_mime_type(response["result"]["content"])
    return contents

def get_all_collection(keyword): 
    url = "https://sunbirdsaas.com/api/content/v1/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "request": {
            "filters": {
                "channel": "013812745304276992183",
                "contentType": ["Collection"],
                "keywords": [keyword]
            }
        }
    }
    response = make_post_api_request(url, headers, data)
    return response
