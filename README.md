# Tracking API
We have an application, with multiple users, for which we want to set up event tracking. Instead of using a tracking service, we have decided to build our own microservice. The microservice is supposed to be able to collect any kind of events; such as user actions and server stats (memory, cpu utilization etc). The collected events need to be aggregated so that it can be analyzed and visualized.

## Setup
1. (Optional) Create virtual environment & activate it
    ```bash 
    python3 -m venv env 
    source env/bin/activate
    ```
2. Install requirements
    ```bash 
    pip install -r requirements.txt 
    ```
3. Change db configuration in settings.py to your setup
4. Apply migrations
    ```bash 
    python3 manage.py migrate
    ```
5. Create superuser
    ```bash 
    python3 manage.py createsuperuser
    ```
6. (Optional) Prefill database with sample data
    ```bash 
    python3 manage.py loaddata data.json
    ```
7. Run server
    ```bash 
    python3 manage.py runserver
    ```
8. Configure Oauth2

#### Oauth2 configuration
The micro service uses Oauth2 for client authentication. Register a new client application as follows:

1. Register a new application on http://127.0.0.1:8000/o/applications/register/ (```Client type``` -> Confidential & ```Authorization grant type``` -> Client credentials)
2. Store your client_id & client_secret securely (they can also be read from the database)
3. Retrieve a new access token for your client using the id and secret (this can be done comfortably in Postman, when selecting OAuth 2.0 as Authorisation[Access Token URL = "http://127.0.0.1:8000/o/token/"; Scope = "read writhe aggregation"]). 
**Important:** if you want to use the Aggregation endpoint (/api/events/) you have to add the aggregation scope. So in the end your token needs to have ```read write aggregation``` as scopes (can be edited in database table ```oauth2_provider_accesstoken```)
4. Use the access token as your Bearer token for all future requests

## Endpoints:
### Tracking endpoint
```/api/track/```

**Request body:**
```json
{
"namespace": "this is namespace",
"name": "this is a name",
"timestamp": "2020-11-12T11:10:00",
"value": 1
} 
```
- namespace: A namespace to group events under e.g. “Frontend”, “Back- end”, “Server-1” (String)
- name: The name of an event e.g. “availableMemory”, “pageView”, “subscribeButtonClick” (String
- timestamp: Datetime
- value: A number that reflects some attribute of the event e.g. For a pageview this could be the amount in seconds the user spent on the page, for button clicks it could be just 1 (integer)

### Aggregation endpoint
```/api/events/<str:namespace>/<str:event_name>?tsMin=42&tsMax=69&granularity=month&aggregationType=avg```

**Route parameters:**
- namespace
- EventName: The event whose data you want to fetch

**Query parameters:**
- tsMin: Start of the time window from which events will be selected (UNIX timestamp)
- tsMax: End of the time window from which events will be selected (UNIX timestamp)
- granularity: The granularity of aggregation. Possible value are: “minute”,
“hour”, "day", “week”, “month”, “year”, “none”
- aggregationType: The method of aggregating values in one granularity
group. Possible values are: “max”, “min”, “avg”. Default is "avg".

**Return data:** \
A list of aggregated events in the format:
```json
{
    "aggregatedTimestamp": "2020-11-12T11:10:00",
    "value": 142.0
```
- aggregatedTimestamp: the lowest timestamp of the granularity group (datetime)
- value: The aggregated value in this granularity group (nueric)

## Next steps
#### Get ready for production:
- Split into main/develop branch
- Create .env & sample.env files for secrets, db config etc & read from it in code
- Improve permissions & add environment_type flag (DEBUG/STAGING/PRODUCTION) to .env and make things like admin page etc. dependent on it
- Dockerize
- Unit/Webtests (Newman)
- Choose Provider (e.g. AWS) to host the database & run staging/production server
- Build pipeline for automated testing, building & deployment with GitHub Actions (ideally)

#### Increase traffic:
- Optimize DB connections
- Find optimal VM configuration
- Look into & possibly use things like a MessageQueue
- Host multiple instances & use a load balancer, maybe shard data onto different databases and/or have different instances handle different regions/namespaces(probable needs middleware then to distribute)
