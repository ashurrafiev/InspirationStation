
# User Engagement Report

[report_engagement.py](report_engagement.py)

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
