
# User Interaction Log

(as logged by [station.js](../server/static/station.js))

Each log line contains three tab-separated values: ISO-formatted UTC timestamp, event name, and additional event information. The latter can be empty.

Example:

```
2023-08-19T09:27:49.083Z	OPEN_OBJECT	middle,72-devils-toenails
```

Here, an `OPEN_OBJECT` event happened at 10:27 AM (British summer time adds +1 to UTC) on Saturday, 19th of August 2023.

Event information is context specific. Following is the description of the events and their respective information.

**Important!** if the interactive page is opened in a browser outside the museum, it will also upload events into the same usage log. Watch for the IP address in `SERVER_RECEIVE_LOG` event info.

### INIT

Museum interactive is loaded. This is the first event after the PC is powered up and successfully started the interactive.

This event is immediately followed by a number of `INFO` events contaning system information.

**Info:** none


### INFO

System information. Provided after each `INIT` event.

**Info:** `variable=value` 

Currently logged variables:

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

A new set of objects is shown on the screen. Usually happens after `PULL_LEVER` or when the page is loaded.

**Info:** the set of three displayed objects, comma-separated: `left-object,middle-object,right-object`


### PULL_LEVER

User pulls the lever to reroll displayed objects. This event should always be followed by `DISPLAY_OBJECTS`.

**Info:** none


### OPEN_OBJECT

User clicked an object to open it.

Every object interaction sequence of events happens between `OPEN_OBJECT` and `CLOSE_OBJECT` events, including editing and posting a story.

**Info:** which box is clicked (left, middle, or right) and clicked object ID: `position,object-id`


### ON_PAGE

User goes to a new UI screen by clicking a button (Back, Next, Cancel, etc.).

The presence of any `ON_PAGE` in an object sequence indicates that user chose _Yes_ to start a story.

**Info:** `ui-page-id`

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

(TBC)
