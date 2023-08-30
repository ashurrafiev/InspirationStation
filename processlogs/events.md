
# User Interaction Log


Usage log is enabled only if `station.html` is opened with `#postlog` parameter, i.e.:
```
/static/station.html#postlog
```

Multiple hash parameters are comma-separated:
```
/static/station.html#postlog,mproxy
```

**Important!** if the interactive page is opened with `#postlog` in a browser outside the museum, it will upload events into the same usage log. Watch for the IP address in `SERVER_RECEIVE_LOG` event info to filter out any impostors.

Monthly user interaction logs can be downloaded as `station-YYYY-MM.zip` files from the moderator dashboard's Downloads page.

Each log line contains three tab-separated values: ISO-formatted UTC timestamp, event name, and additional event information. The latter can be empty.

Example:

```
2023-08-19T09:27:49.083Z	OPEN_OBJECT	middle,72-devils-toenails
```

Here, an `OPEN_OBJECT` event happened at 10:27 AM (British summer time adds +1 to UTC) on Saturday, 19th of August 2023.

Event information is context specific. The following is the description of events and their respective information.
See [station.js](../server/static/station.js) for implementation details.

### INIT

Museum interactive is loaded. This is the first event after the PC is powered up and successfully started the interactive.

This event is immediately followed by a number of [`INFO`](#info) events contaning system information.

**Info:** none


### INFO

System information. Provided after each [`INIT`](#init) event.

**Info:** `variable=value` 

Currently, the following variables are logged:

| variable | description |
| :--- | :--- |
| `scriptVersion` | current `station.js` version |
| `userAgent` | browser version as provided by JavaScript |
| `devicePixelRatio` | expected to be `1` for the interactive |
| `mediaPath` | where the videos and images are downloaded from |


### DATA_LOADED

Indicates that the interactive received object data from the server. The database is reloaded every 30 min.

**Info:** none


### DISPLAY_OBJECTS

A new set of objects is shown on the screen. Usually happens after [`PULL_LEVER`](#pull_lever) or when the page is loaded.

**Info:** the set of three displayed objects, comma-separated: `left-object,middle-object,right-object`


### PULL_LEVER

User pulls the lever to reroll displayed objects. This event should always be followed by [`DISPLAY_OBJECTS`](#display_objects).

**Info:** none


### OPEN_OBJECT

User clicked an object to open it.

Every object interaction sequence of events happens between `OPEN_OBJECT` and [`CLOSE_OBJECT`](#close_object)
events, including editing and posting a story.

**Info:** which box is clicked (left, middle, or right) and clicked object ID: `position,object-id`


### ON_PAGE

User goes to a new UI screen by clicking a button (Back, Next, Cancel, etc.).

The presence of any `ON_PAGE` in an object sequence indicates that user chose _Yes_ to start a story.

**Info:** opened UI page: `ui-page-id`

List of UI pages:

| page ID | description |
| :--- | :--- |
| `ui-page-open` | Do you want to start your story with this object? |
| `ui-page-q1` | What do you see? |
| `ui-page-q2` | What do you notice? |
| `ui-page-q3` | What does it make you think or wonder? |
| `ui-page-done` | Here's the story you've begun. |
| `ui-page-confirm-share` | Continue to save your story? |
| `ui-page-send` | Connecting... |
| `ui-page-send-rejected` | Oops! We can't accept your story. Did you use bad words? |
| `ui-page-send-err` | Oops! That didn't work. |
| `ui-page-qr` | You can point your phone at this code... |
| `ui-page-confirm-close` | Are you sure you want to abandon your story? |


### DONE_CHECK

The status of completion-checking the story. This check happens when user enters the "Done" page,
therefore, this event should appear after each `ON_PAGE ui-page-done`.

**Info:** Completion check status: `status`.

| status | description |
| :--- | :--- |
| `ok` | All questions are answered. |
| `unfinished` | Some questions are not answered. |
| `too-long` | Oops! Your story is too long. Please shorten it a bit. |


### POST_STORY

The story is sent to the server. The upload may still fail with `ON_PAGE ui-page-send-rejected` (if bad words are detected)
or `ON_PAGE ui-page-send-err` (if there is a connection or server error).

**Info:** ID of the museum object: `object-id`.


### STORY_UID

The story has been successfully uploaded to the server.

**Info:** UID of the submitted story: `story-uid`

UID can be used to identify the story in the moderator dashboard.


### TIMEOUT

The UI has timed out because of no input from the user for 45 seconds. This event is always followed by [`CLOSE_OBJECT`](#close_object).

**Info:** UI page where this happened:`ui-page-id`

See [`ON_PAGE`](#onpage) for the list of page IDs.


### CLOSE_OBJECT

The object has been closed either by the user or by timeout. This event ends the interaction sequence started
by the [`OPEN_OBJECT`](#open_object) event.

**Info:** ID of the closed object: `object-id`.

The ID should match the most recent `OPEN_OBJECT` event.


### SERVER_RECEIVE_LOG

The list of events has been received by the server. This event is added _after_ all the events contained in the upload.

> The `SERVER_RECEIVE_LOG` event is printed by the server using the server clock for the timestamp.

**Info:** IP address, from which the server received the list of events; also "empty" if the list contained no events: `ip=sender-ip[,empty]`
