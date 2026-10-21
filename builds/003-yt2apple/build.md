# yt2apple

A small browser extension for taking a personal YouTube Music queue toward an Apple Music playlist.

## The idea

Recommendations often live in one service while listening happens in another. The useful bridge is the song metadata: capture it, clean it up, let the listener review it and hand it to a transfer service.

## What is built

- Capture loaded songs from YouTube Music's queue in Chrome or Edge.
- Review checked tracks and edit song details before export.
- Download a CSV or send the selected source metadata to TuneMyMusic.
- Use an optional Apple catalog matcher to inspect candidates and retry unresolved songs.

The extension preserves manual choices and supports session backups. Optional catalog matching uses request spacing, bounded concurrency and cached searches. Audio is not downloaded or transcribed.

## Where it stands

The default workflow delegates Apple matching and transfer to TuneMyMusic. The extension itself does not create an Apple Music library playlist. Ambiguous titles, singers and recording variants still need review; a match is not a guarantee that the intended recording was selected.

The documented remaining verification step is a signed-in, end-to-end personal transfer. This is a working prototype, not a broad catalog-accuracy benchmark.
