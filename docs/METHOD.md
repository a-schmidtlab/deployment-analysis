# Method

## Arrival and activation

Each export row describes one image. The activation timestamp is taken from
`Bild Aktivierungszeitpunkt` (format `dd.mm.yyyy HH:MM:SS`; other formats are
parsed as a fallback). The export carries no arrival date, only the time of
day as a prefix of the IPTC instruction, e.g. `[23:51:45] *** World Rights ***`.

The arrival timestamp is reconstructed as

    arrival = date(activation) + time_of_day(IPTC)

and moved to the previous day if this lies more than 12 hours after the
activation:

    if arrival - activation > 12 h:  arrival -= 1 day

The delay is `activation - arrival` in minutes.

## Midnight crossing and clock skew

An image arriving at 23:58 and activated at 00:03 carries the next day's
activation date, so the same-day combination (23:58 on the activation day)
lies almost 24 hours after the activation and is shifted back by one day:
delay 5 minutes.

The IPTC time and the activation timestamp come from different systems. In the
real exports a few thousand rows have an IPTC time a few seconds to a few
hours *after* the activation. Version 1.x shifted every such row to the
previous day and thereby produced delays of almost 24 hours. Since version 2.0
these rows keep the same day, get a negative delay and are dropped (reported
as "negative").

Effect on the five real exports of 2024/2025 (1.79 million rows, kept in a
private repository):

| Rule | Usable rows | Dropped as negative | Mean delay | Median | 95th percentile | Delays > 20 h |
|------|------------:|--------------------:|-----------:|-------:|----------------:|--------------:|
| 1.x: every inversion is a midnight crossing | 1,659,621 | 0 | 10.6 min | 4.1 min | 16.0 min | 1,720 |
| 2.0: only inversions > 12 h | 1,655,036 | 4,585 | 7.5 min | 4.1 min | 15.2 min | 111 |

The median is unaffected; the mean of version 1.x was inflated by about
3 minutes.

## Dropped rows

| Reason | Rule |
|--------|------|
| unparseable | no `[HH:MM:SS]` prefix in the IPTC field, or no valid activation timestamp |
| negative | arrival after activation (see above) |
| above maximum | delay above `--max-delay` (default 1440 minutes) |

The export for the first quarter of 2024 lacks the IPTC time prefix in about a
third of its rows; these rows cannot be evaluated. A warning is logged when
more than 5 % of the rows of a load are unparseable.

## Aggregation

Heatmap cells are the arithmetic mean of the delays of all images whose arrival
falls into the row period and the hour of day. Empty cells (no images) are
white. The colour scale is clipped to the 10th–95th percentile of the cell
values for timelines and to the 5th–95th percentile for profiles, so that
single outliers do not hide the pattern; the statistics line always reports
the unclipped values.

Weeks are ISO weeks (Monday to Sunday, week 1 contains the first Thursday of
the year). Around New Year the ISO year can differ from the calendar year;
such weeks are labelled `W01/25` in the GUI.

## Duplicate files

When several files are loaded, each file's content is hashed independently of
header row, delimiter and encoding. A file identical to one already loaded is
skipped with a warning. Partially overlapping exports are not detected; their
overlapping rows are counted twice.
