---
title: "Fusion Dancing Local Community Integration"
alias: "local-scenes"
---

# Integrating a local community

To add your local community with your regular socials and other smaller events on a dedicated sub-page like https://fusion-dancing.eu/frankfurt, you need to send the link of a Google Sheet with all your events to events[at]fusion-dancing.eu

## Google Sheet

The Sheet link needs to be a read only link that is accessible without login. It needs to contain the columns:
- Title
    - The title of your event
    - Example: Taster & Social
- Start
    - Start date and time
    - Format: `YYYY-MM-DD HH:MM`
    - Example: `2025-03-30 18:00`
- End
    - End date and time
    - Format: `YYYY-MM-DD HH:MM`
    - Example: `2025-03-30 18:00`
- Location
    - Where is the glory happening?
    - Example: Awesome Pub, 5th Avenue
- Added
    - Date when you added the event (relevant for RSS feed generation)
    - Format: `YYYY-MM-DD`
    - Example: `2025-03-30`
- Link
    - Optional link to an event page
    - Example: https://awesome-fusion-social.berlin


See the [Google Sheet for the Darmstadt socials](https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/edit?usp=sharing) as an example.

Don't like Google? Sounds fair. You can instead provide a public link to any CSV file that follows the schema above.

## Updating events

You can add and update events in your Google Sheet as you please.
The events are fetched every 15 minutes from your Google Sheet.
If the events do not show up after those 15 minutes, contact events[at]fusion-dancing.eu

## Custom intro text

If you want, you can also send along a custom intro text that you would like to see displayed on your local community page above the list of events.