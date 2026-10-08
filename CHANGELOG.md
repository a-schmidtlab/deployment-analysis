# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/), versions: [SemVer](https://semver.org/).

## [2.0.0] – 2026-10-08

Rewrite. One installable package replaces the 2,900-line script, the unused
`src/` prototype and nine build scripts.

### Fixed
- **Clock skew counted as almost 24 h delay.** An IPTC time slightly after the
  activation was treated as a midnight crossing. Over the real exports this
  raised the mean delay from 7.5 to 10.6 minutes. See [docs/METHOD.md](docs/METHOD.md).
- Identical files loaded twice (e.g. the same export with and without header)
  were counted twice; they are now skipped.
- **Week buttons showed the following week** in years whose 1 January falls
  on Tuesday to Thursday (2025, 2026, ...): the buttons used ISO week numbers,
  the date range was computed with `%W` week numbers.
- CSV files were always decoded as UTF-8; Windows-1252 exports failed to load.
  The encoding is now detected.
- Exports without a header row failed with "could not identify required
  columns"; they are now read with the standard column order.
- Month buttons were built for the first year of the data only; months of
  later years were unreachable.
- After import the heatmap was titled "Yearly View for None", and month
  selections were labelled as yearly views.
- Worker threads opened message boxes and swapped the analyzer's shared data
  (`cleaned_data`) while other threads read it. Loading now runs in one
  worker thread that hands its result to the main thread through a queue;
  pivoting and plotting happen on the main thread only.
- `pyplot` figures were never closed (memory grew with every view change) and
  the matplotlib backend was switched at runtime for every plot.
- The progress bar ran a fake two-second animation thread per status message.
- The command-line mode returned exit code 0 on failure.
- The heatmap code existed three times with diverging colour maps and limits.

### Changed
- Command line: `deployment-analyzer FILE... [-o heatmap.png] [-g granularity]
  [--year/--month/--week] [--export-csv]`; several files at once; exit codes
  0 (ok), 1 (no data in period), 2 (error).
- Statistics include median and 95th percentile.
- Column names of exported data are English (`arrival`, `activation`,
  `delay_minutes`, ...).
- Windows build: one PyInstaller spec and `packaging/build.ps1`.
- License: PolyForm Noncommercial 1.0.0.

### Removed
- Company exports, the SQLite database and logs from the repository and its
  history (moved to a private repository).
- Committed executables and build logs, `launcher.py`, `standalone.py`,
  `app_config.ini` support, the Dash dashboard prototype under `src/`
  (its dependencies `dash`, `plotly`, `scipy` were never declared).

### Added
- Test suite (64 tests) with synthetic data, CI on Linux and Windows.
- `docs/METHOD.md`, `CITATION.cff`, synthetic `examples/sample_data.csv`.

## [1.1.1] – 2025-03-03

Last version of the original script (`deployment-analyse.py`) with Windows
release folder.
