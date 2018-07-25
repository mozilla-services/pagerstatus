from chalice import Chalice
from chalice import NotFoundError, BadRequestError
from chalicelib import settings, pagerduty, statuspage

app = Chalice(app_name="pagerstatus")


@app.route("/{pagerduty_account}", methods=["POST"])
def handle_webhook(pagerduty_account):
    try:
        pagerduty_key = settings.pagerduty_credentials[pagerduty_account.lower()]
    except KeyError:
        raise NotFoundError(f"Configuration for {pagerduty_account} not found")

    try:
        will_sync = pagerduty.incident_acknowledged_or_resolved(
            app.current_request.json_body
        )
    except:
        raise BadRequestError()

    if will_sync:
        sync(pagerduty_key)
        return ["Performed sync"]
    else:
        return ["No need to sync"]


def sync(pagerduty_key):
    components_from_pagerduty = pagerduty.components_with_incidents(pagerduty_key)

    (
        statuspage_components,
        statuspage_components_to_incidents,
    ) = statuspage.components_and_incidents()

    components_needing_close = statuspage_components - components_from_pagerduty
    components_needing_open = components_from_pagerduty - statuspage_components

    for component in components_needing_close:
        incident = statuspage_components_to_incidents[component]
        statuspage.close_incident(component, incident)
    for component in components_needing_open:
        statuspage.open_incident(component)
