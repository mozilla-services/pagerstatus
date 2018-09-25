import re
import requests


def incident_acknowledged_or_resolved(payload):
    for message in payload["messages"]:
        if (
            message["event"] == "incident.acknowledge"
            or message["event"] == "incident.resolve"
        ):
            return True
    return False


# TODO: Handle Pagination
def _get_acknowledged_incidents(api_key):
    url = "https://api.pagerduty.com/incidents"
    params = {
        "limit": "100",
        "statuses[]": "acknowledged",
        "time_zone": "UTC",
        "include[]": "first_trigger_log_entries",
    }
    headers = {
        "Authorization": f"Token token={api_key}",
        "Accept": "application/vnd.pagerduty+json;version=2",
    }
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        print(f"Received error {r.status_code} for {url} with body:\n{r.content}")
        r.raise_for_status()
    incidents = r.json()["incidents"]
    return incidents


def _incident_component(incident):
    try:
        tags = incident["first_trigger_log_entry"]["channel"]["details"]["tags"]
    except (KeyError, TypeError):
        print(f"It has no tags. Incident details were:\n{incident}")
        return None
    # for datadog pagerduty returns comma seperated string for tags
    # for pingdom it returns list, which we'll reformat to match datadog
    if isinstance(tags, list):
        tags = ",".join(tags)
    match = re.search(r"component[:_](\w+)", tags)
    if match:
        component = match.group(1)
        print(f"It is tagged component {component}")
        return component
    else:
        print("No tags match")
        return None


def components_with_incidents(api_key):
    components = set()
    incidents = _get_acknowledged_incidents(api_key)
    print(f"Found {len(incidents)} pagerduty incidents")
    for incident in incidents:
        print(f"For pagerduty incident {incident['id']}")
        component = _incident_component(incident)
        if component:
            components.add(component)
    return components
