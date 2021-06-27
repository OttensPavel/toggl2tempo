# Toggl2Tempo

Toggl2Tempo is a desktop application to sync work logs between Toggl and JIRA Tempo.

## Installation

### On Windows:

**ATTENTION!** Windows x32 doesn't support.

[Download](https://github.com/OttensPavel/toggl2tempo/releases) and install last release of toggl2tempo.

### On Linux: 
TODO: Coming soon 

## Setup
Sorry, but UI for settings isn't complete yet.
But all settings, which you need, aren't changed usually therefore you should setup it only one time. :)

### JIRA
There are following settings:
* host: host of your Cloud JIRA instance, for examples: _https://cloud.atlassian.net_
* user: email which you use to log in JIRA, for example: _myname@cloud.atlassian.net_
* token: JIRA API token, - please see below.

#### Create an API token
Create an API token from your Atlassian account:
* Log in to https://id.atlassian.com/manage/api-tokens.
* Click Create API token.
* From the dialog that appears, enter a memorable and concise *Label* for your token and click *Create*.
* Click *Copy to clipboard*, then paste the token to "//jira/token" setting

Official manual from Atlassian you can find [here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html)

### Tempo
You need to generate Tempo API token.
Please see [official manual](https://tempo-io.atlassian.net/wiki/spaces/KB/pages/199065601/How+to+use+Tempo+Cloud+REST+APIs)
paragraph _Create a personal authorization token_. 

### Toggl
Setup of Toggl is easier - you need only API token which you can found on page of you profile:
https://toggl.com/app/profile

## Used software
* NSIS (Nullsoft Scriptable Install System) https://nsis.sourceforge.io/
  * Inetc_plug-in https://nsis.sourceforge.io/Inetc_plug-in
