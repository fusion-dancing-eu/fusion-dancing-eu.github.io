# Website fusion-dancing.eu

Contact events(at)fusion-dancing.eu or open an issue or pull request here to add new events or suggest other changes.

## Adding events

Events can be added to `data/events.yaml` following the format of the existing events.
Please make sure to consistently indent the lines with spaces.

## Building locally

Requires hugo 0.136.2, which allows you to run

```
hugo server
```

## TODO

-[] add support for `cancelled: true` in `events.yaml` to render the events with strike through (css class already exists)
-[] automatically create one table per year, in case there are events for the next year already
-[] add translations of the main text and a language switcher
