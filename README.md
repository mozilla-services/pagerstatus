# What is Pagerstatus?

Pagerstatus is a service to automatically update [Atlassian Statuspage](https://www.statuspage.io/) based on [Pagerduty](https://www.pagerduty.com/) incidents.

There are a number of frustrating aspects to Statuspage’s built-in Pagerduty integration.

* None of the setup can be automated
* You can only connect one Pagerduty account with Statuspage
* You have to create a new incident template for each component
* You have to create a plethora of Pagerduty services, since they map 1-to-1 with Statuspage components
* You have to choose betYouen Statuspage potentially creating multiple simultaneous incidents for the same component, or Statuspage potentially adding unrelated outages for two components to the same incident

Pagerstatus solves these problems!

* Since setup is driven by tags in your monitoring tools and pagerduty webhooks, which are both exposed via APIs, it can be automated
* As many Pagerduty accounts as needed can send to the service 
* You don’t have to create any incident templates.
* You don’t have to change anything in your Pagerduty services beyond enabling the outgoing webhook. You do have to edit each monitor that you want to trigger a Statuspage incident, though.
* It implements logic so that only one incident can be open at once per component + multiple components can have incidents open at once

# Service Design

Pagerstatus is written using [Chalice](https://github.com/aws/chalice), a Python "serverless" framework from AWS. It's deployed as a Lambda function behind API Gateway,

The basic logic is straightforward. When a webhook is received from Pagerduty, iterate over each message in the payload. Then, if any Pagerduty incidents were triggered or resolved

1. Fetch all open incidents from Statuspage. Ignore any affecting multiple components. Ignore any that do not have a string in the body denoting it was created by this tool.
1. Fetch all open incidents from Pagerduty. Ignore any that do not have the component tag.
1. If there are any components in Statuspage that are not in Pagerduty, look up their incidents and close them.
1. If there are any components in Pagerduty that are not in Statuspage, create incidents for them.


# Deploy It

Before you begin, you'll need a few pieces of information

* A Pagerduty v2 API key. This can be read-only.
* The name of your pagerduty account.

If you have multiple Pagerduty accounts, collect that for each one. You'll also need

* Your Statuspage's page ID
* A Statuspage API key.

Multiple Statuspage's are not supported. As a workaround, you can deploy this service multiple times.

Clone this repository and make it your working directory.

Modify `.chalice/config.json`. Set `STATUSPAGE_PAGE` and `STATUSPAGE_KEY` to your page id and API key.

For each pagerduty account, create a variable that begins with `PD_ACCOUNT_` and ends with your account name. For instance, if your account name is _hugops_ create the variable `PD_ACCOUNT_HUGOPS`. Set the value of that variable to the corresponding API key.

[Ensure your aws credentials are configured correctly and install chalice](http://chalice.readthedocs.io/en/latest/quickstart.html)

Run `chalice deploy`.

Note the URL it shows. That's where you can access pagerstatus.

# Use It

## Configuring Statuspage

No special configuration is needed in Statuspage. Just create your components and note their IDs for use in tags later.

## Configuring Pagerduty

Take

## Configuring your monitors

Pagerstatus has been tested to work with Datadog and Pingdom.

In datadog, tag each monitor with the form `component:component-id`.

In Pingdom, tag each check with the form `component_component-id`.