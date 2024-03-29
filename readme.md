# Story Inspiration Station

https://inspire.storyweb.info/

Content:

* `server/` backend web server app.
* `docker-compose.yaml` docker container for the backend web server app.
* `traefik.toml` Traefik setup for the backend web server app.
* `mediaproxy/` local proxy server for the kiosk PC.
* `parsedata/` helper utility for parsing object data from an Excel/CSV to JSON database.
* `processlogs/` user interaction log [documentation](processlogs/events.md) and [report generation scripts](processlogs/readme.md). 
* `scp_server.sh` helper utility for uploading backend app sources to the server.

Excluded assets (to be added manually):
* `server/static/Lora-Bold.ttf`
* `server/static/Lora-Regular.ttf`
* `server/static/OpenSans-Bold.ttf`
* `server/static/OpenSans-Regular.ttf`

You can download these fonts here: [Lora](https://fonts.google.com/specimen/Lora), [Open Sans](https://fonts.google.com/specimen/Open+Sans).

Object videos and cover images are stored on the S3 cloud.


## Backend Web Server

### Setting up local development environment

Install requirements:

```
cd server
pip install -r requirements.txt
```

Create a PostgreSQL database however you like. Use `storyweb.sql` to set up database structure.

Rename `example.config.json` to `config.json` and add database credentials to the `"database"` section.

Generate JWT secret key and add it to `config.json`. You can do it in Python using:

```
import secrets
secrets.token_urlsafe(64)
```

> Note: changing JWT key will logout all users from the moderator dashboard.

You don't need to use docker in the local development environment. Run without docker:

```
python3 inspire.py
```

Open http://localhost:8080 in a browser.


### Setting up production environment using docker

SSH to the server, create a directory for the web server app, for example:
```
mkdir /server/apps/inspiration_station
```

Copy `docker-compose.yaml`, `traefik.toml` and the entire `server/` directory to that folder.

Make sure `server/config.json` has production configuration and doesn't have `"devMode": true`.

Create an empty `acme.json` file next to `docker-compose.yaml` and `chmod` to `600`:
```
touch acme.json
chmod 600 acme.json
```

Start docker container:
```
docker-compose up -d
```

You can later restart the docker using `docker-compose down` followed by `docker-compose up -d`.
The docker must be restarted every time you make changes to Python sources!


# Downloadable Data Format

Some data can be download in JSON or CSV format (zipped) from the moderators' dashboard Downloads section.

### Full database of stories

| field/column | description |
| :--- | :--- |
| **uid** | Story unique ID, used for story URL |
| **obj** | Object ID, for example `2-ntomo-mask` |
| **q1** | Answer to Question 1 |
| **q2** | Answer to Question 2 |
| **q3** | Answer to Question 3 |
| **time** | UTC time of posting the story |
| **mod** | Moderation status: `new`, `block`, `ok`, or `star` |
| **ip** | IP address from which the story has been posted from (expected Museum IP address) |
| **editor** | User name of the moderator who reviewed the story, or `null` |
| **upd_time** | UTC time of moderation, or `null` if is hasn't been moderated |

### Database of museum objects

| field/column | description |
| :--- | :--- |
| **id** | Object ID, for example `2-ntomo-mask`. Should be the same as the video file name and cover image file name |
| **name** | Displayed name, for example `N’tomo Mask` |
| **fact** | Text for interactive |
| **collectionNumber** | TWAM collection number or `??` |

### User Interaction Logs

See [usage log documentation](processlogs/events.md).
