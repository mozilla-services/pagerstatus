import os
import requests
import poyo
from chalicelib import settings


def _request(path, method="get", data=None):
    url = "https://api.statuspage.io/v1/pages/%s/%s" % (settings.statuspage_page, path)
    headers = {"Authorization": "OAuth %s" % settings.statuspage_key}
    if method == "patch":
        r = requests.patch(url, headers=headers, data=data)
    elif method == "post":
        r = requests.post(url, headers=headers, data=data)
    else:
        r = requests.get(url, headers=headers)
    if r.status_code != 200 and r.status_code != 201:
        print(f"Received error {r.status_code} for {url} with body:\n{r.content}")
        r.raise_for_status()
    return r.json()


def _get_incidents():
    return _request("incidents/unresolved.json")


def _create_incident(name, body, incident_status, component_id, component_status):
    data = {
        "incident[name]": name,
        "incident[body]": body,
        "incident[status]": incident_status,
        "incident[component_ids][]": component_id,
        f"incident[components][{component_id}]": component_status,
    }
    _request("incidents.json", method="post", data=data)


def _update_incident(incident_id, incident_status, component_id, component_status):
    data = {
        "incident[status]": incident_status,
        "incident[component_ids]": component_id,
        f"incident[components][{component_id}]": component_status,
    }
    _request(f"incidents/{incident_id}.json", method="patch", data=data)


def _we_created_incident(incident):
    # filter out incidents that were not opened by this tool
    if settings.watermark in incident["incident_updates"][-1]["body"]:
        print("We opened it")
        return True
    else:
        print("We did not open it")
        return False


def _component_from_incident(incident):
    return incident["incident_updates"][-1]["affected_components"][-1]["code"]


def components_and_incidents():
    components = set()
    components_to_incidents = dict()
    incidents = _get_incidents()
    print(f"Found {len(incidents)} statuspage incidents")
    for incident in incidents:
        print(f"Found statuspage incident {incident['id']}")
        if _we_created_incident(incident):
            affected_component = _component_from_incident(incident)
            print(f"Affected component is {affected_component}")
            components.add(affected_component)
            components_to_incidents[affected_component] = incident["id"]
    return (components, components_to_incidents)


def close_incident(component_id, incident_id):
    print(
        f"Resolving statuspage incident {incident_id} and marking component {component_id} operational"
    )
    _update_incident(incident_id, "resolved", component_id, "operational")


# TODO allow choosing template based on a tag
# TODO allow interpolating component name in incident name and body
def open_incident(component_id):
    template_path = f"{os.path.dirname(__file__)}/incident_templates/default.yml"
    template = poyo.parse_string(open(template_path, "r").read())

    # add our watermark so later we can identiy this incident as being created by this tool
    body = f"{template['body']}\n{settings.watermark}"

    print(
        f"Opening statuspage incident for component {component_id} and marking it {template['component_status']}"
    )
    _create_incident(
        template["name"],
        body,
        template["incident_status"],
        component_id,
        template["component_status"],
    )
