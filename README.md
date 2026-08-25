# Website fusion-dancing.eu

Contact events(at)fusion-dancing.eu or open an issue or pull request here to add new events or suggest other changes.

## Adding events

Events live in `data/events/`, with one file per year: `data/events/2026.yaml` holds every event starting in 2026.
Add your event to the file of the year it starts in, following the format of the existing events.
Each file is a plain list of events, the year itself comes from the file name.
If the year has no file yet, create `data/events/<year>.yaml` and start the list there.
Please make sure to consistently indent the lines with spaces.

* `name`: Title of the event, e.g. "Awesome-Town Fusion Weekend"
* `start`: Day the event starts in the format `YYYY-MM-DD`, e.g. "2020-01-31"
* `end`: Last day of the event in the format `YYYY-MM-DD`, e.g. "2020-01-31"
* `location`: City and country the event takes place in, e.g. "Bern, Switzerland"
* `link`: Event website with more details, e.g. "https://awesome-town-fusion-weekend.nl"
* `added`: The date of the day this event was added (or last updated) in the format `YYYY-MM-DD` to differentiate newly added events in the RSS feed, e.g. "2024-12-31"

When logged in on GitHub.com, you can [browse the year files here](https://github.com/fusion-dancing-eu/fusion-dancing-eu.github.io/tree/main/data/events) and edit the one you need, click on "Commit changes..." selecting "Create a new branch for this commit and start a pull request" to save your changes and have them reviewed before publication.

## Building locally

Requires [Hugo](https://gohugo.io) (tested with version 0.136.2), which allows you to run

```
hugo server
```

## TODO

- [ ] add translations of the main text and a language switcher
