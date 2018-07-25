import os
import re

statuspage_page = os.environ["STATUSPAGE_PAGE"]
statuspage_key = os.environ["STATUSPAGE_KEY"]
watermark = "⛈"
default_incident_template = "default.yml"

pagerduty_credentials = dict()

for name, value in os.environ.items():
    match = re.match("PD_ACCOUNT_(.*)", name)
    if match:
        account = match.group(1).lower()
        pagerduty_credentials[account] = value
