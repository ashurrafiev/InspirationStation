
# User Engagement Report tools

These Python scripts are used to process [user interaction logs](events.md).

### Engagement by object

[report_engagement.py](report_engagement.py)

Reports the total number of interactions per museum object in the following categories:
* **Shown** How many times an object has been randomly displayed after the lever is pulled.
* **Clicked** How many times an object has been clicked on the main screen.
* **Started story** User clicked _Yes_ to start a story with the object.
* **Finished story** User answered something to all questions.
* **Posted story** User agreed to save the story.

Usage: see [command line arguments](#command-line-arguments)


### Engagement heatmap

[report_heatmap.py](report_heatmap.py)

Creates a heatmap plot of user engagement frequency throughout the day. Each histogram bin is represents 5 minutes (10 minutes for `SERVER_RECEIVE_LOG`).

HTML version includes cumulative graph for the whole period followed by daily graphs. CSV version contains only cumulative information for the whole period.

* **Interactive is online** `SERVER_RECEIVE_LOG` sent every 10 min after the interactive comes online until the power is down.
* **Lever pulled** `PULL_LEVER`
* **Object clicked** `OPEN_OBJECT`
* **Editing or navigating story UI** `ON_PAGE` counts every UI page, including going back and forth, so editing one story should go through at least 4 pages.
* **Story posted** `POST_STORY`

Usage: see [command line arguments](#command-line-arguments)


### Command line arguments

Both tools use the same command line options.

#### Usage:

```
python3 report_engagement.py INPUT [-h] [-o OUTPUT] [--html|--csv] [--from T_START] [--until T_END] [-d DAY] [-z TIMEZONE]
```

| argument | description |
| :--- | :--- |
| *INPUT* | (required) Input [user interaction log](events.md) file |
| `-h`<br/>`--help` | Show help message and exit |
| `-o`&nbsp;*OUTPUT*<br/>`--output`&nbsp;*OUTPUT* | Output file name. If not specified, the output is written to the terminal. |
| `--html` | Set output format to HTML. |
| `--csv` | Set output format to CSV. |
| `--from`&nbsp;*T_START* | Filter events that are later than (or equal to) *T_START* timestamp. Format: `yyyy-mm-ddThh:mm[:ss[.ff]]` |
| `--until`&nbsp;*T_END* | Filter events that are earlier than *T_END* timestamp. Format: `yyyy-mm-ddThh:mm[:ss[.ff]]` |
| `-d`&nbsp;*DAY*<br/>`--day`&nbsp;*DAY* | Filter events for one specific day. Overwrites `--from` and `--until`. Format: `yyyy-mm-dd` |
| `-z`&nbsp;*TIMEZONE*<br/>`--timezone`&nbsp;*TIMEZONE* | (integer) All timestamps are in UTC by default. Convert the timezone by adding *TIMEZONE* number of hours to all timestamps. For the UK, use `-z 0` for winter logs (GMT) and `-z 1` for summer logs (BST); `-z 0` is the default. |

If the output format (`--html` or `--csv`) is not specified, the tool tries to deduce the format from the output file extension.

#### Example:

```
python3 report_engagement.py logs/station-2023-08.txt -o reports/engagement.html --from 2023-08-21T00:00 --until 2023-08-28T00:00 -z 1
```
