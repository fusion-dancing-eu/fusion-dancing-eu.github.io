from copy import deepcopy
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import requests
import re
import yaml

HERE = Path(__file__).parent


def slugify(text: str) -> str:
    # 1) lowercase
    text = text.lower()
    # 2) spaces → hyphens
    text = text.replace(" ", "-")
    # 3) remove any char that’s not a–z or hyphen
    text = re.sub(r"[^a-z0-9-]", "", text)
    # 4) collapse multiple hyphens and strip leading/trailing
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def parse_time(ts: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


@dataclass
class ScheduledEvent:
    # the id of the scheduled event
    id: str

    # the guild id which the scheduled event belongs to
    guild_id: str

    # the name of the scheduled event (1-100 characters)
    name: str

    # the time the scheduled event will start
    scheduled_start_time: datetime

    # the privacy level of the scheduled event
    privacy_level: int

    # the status of the scheduled event SCHEDULED 1, ACTIVE 2, COMPLETED 3, CANCELED 4
    status: int

    # the type of the scheduled event STAGE_INSTANCE 1, VOICE 2, EXTERNAL 3
    entity_type: int

    # the channel id in which the scheduled event will be hosted, or null if scheduled entity type is EXTERNAL
    channel_id: Optional[str] = None

    # the id of the user that created the scheduled event
    creator_id: Optional[str] = None

    # the description of the scheduled event (1-1000 characters)
    description: Optional[str] = None

    # the time the scheduled event will end, required if entity_type is EXTERNAL
    scheduled_end_time: Optional[datetime] = None

    # the id of an entity associated with a guild scheduled event
    entity_id: Optional[str] = None

    # additional metadata for the guild scheduled event (e.g. location for type EXTERNAL)
    entity_metadata: Optional[Dict[str, Any]] = None

    # the user that created the scheduled event
    creator: Optional[Dict[str, Any]] = None

    # the number of users subscribed to the scheduled event
    user_count: Optional[int] = None

    # the cover image hash of the scheduled event
    image: Optional[str] = None

    # the definition for how often this event should recur
    recurrence_rule: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ScheduledEvent":

        return ScheduledEvent(
            id=data["id"],
            guild_id=data["guild_id"],
            channel_id=data.get("channel_id"),
            creator_id=data.get("creator_id"),
            name=data["name"],
            description=data.get("description"),
            scheduled_start_time=parse_time(data["scheduled_start_time"]),
            scheduled_end_time=parse_time(data.get("scheduled_end_time")),
            privacy_level=data["privacy_level"],
            status=data["status"],
            entity_type=data["entity_type"],
            entity_id=data.get("entity_id"),
            entity_metadata=data.get("entity_metadata"),
            creator=data.get("creator"),
            user_count=data.get("user_count"),
            image=data.get("image"),
            recurrence_rule=data.get("recurrence_rule"),
        )

    @property
    def links(this):
        return extract_https_urls(this.description)


def fetch_from_discord() -> list[ScheduledEvent]:
    guild_id = os.getenv("DISCORD_GUILD_ID")
    bot_token = os.getenv("DISCORD_BOT_TOKEN")

    url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events"
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    discord_events = [ScheduledEvent.from_dict(event) for event in response.json()]
    return discord_events


def is_relevant_discord_event(event: ScheduledEvent) -> bool:
    # If status is not SCHEDULED or ACTIVE
    if event.status not in [1, 2]:
        return False

    # If type is not EXTERNAL
    if event.entity_type != 3:
        return False

    if event.scheduled_end_time is None:
        return False

    now_utc = datetime.now(timezone.utc)
    if event.scheduled_end_time.tzinfo is None:
        event_end = event.scheduled_end_time.replace(tzinfo=timezone.utc)
    else:
        event_end = event.scheduled_end_time
    if event_end and event_end < now_utc:
        return False

    if event.scheduled_start_time.tzinfo is None:
        event_start = event.scheduled_start_time.replace(tzinfo=timezone.utc)
    else:
        event_start = event.scheduled_start_time
    if event_start and event_start < now_utc:
        return False

    if event.recurrence_rule is not None:
        return False

    if not event.links:
        return False

    return True


def matches_existing_event(
    event: ScheduledEvent, existing_events: dict[str, list]
) -> bool:
    """True if the given event matches any of the existing events."""
    year = event.scheduled_start_time.year
    existing_events_that_year = existing_events.get(year)
    if not existing_events_that_year:
        return False
    matching_events = [
        e
        for e in existing_events_that_year
        if event.name == e["name"] or event.id == e.get("discord_event_id", None)
    ]
    return matching_events


def extract_https_urls(text):
    """
    Extracts all substrings starting with 'https://' up to the next whitespace or
    quote-like delimiter.

    :param text: The input string possibly containing URLs.
    :return: A list of all matched https URLs.
    """
    # This regex matches 'https://' plus any number of characters that are not
    # whitespace or certain punctuation that typically ends a URL.
    pattern = r'https://[^\s\'"<>]+'
    return re.findall(pattern, text)


def add_events(existing_events: dict[str, list], new_events: list[ScheduledEvent]):
    """Add new events to the YAML friendly dictionary with already known events."""
    updated_events = deepcopy(existing_events)
    # Add new events to the correct year
    for e in new_events:
        year = e.scheduled_start_time.year
        new_event = {
            "name": e.name,
            "start": e.scheduled_start_time.strftime("%Y-%m-%d"),
            "end": (
                e.scheduled_end_time.strftime("%Y-%m-%d")
                if e.scheduled_end_time
                else None
            ),
            "location": (
                e.entity_metadata.get("location") if e.entity_metadata else None
            ),
            # Just blindly take the first link from the description
            "link": e.links[0],
            "added": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "discord_event_id": e.id,
        }
        updated_events.setdefault(year, []).append(new_event)
    return updated_events


def remove_year_in_name(event: ScheduledEvent) -> ScheduledEvent:
    """If the year the event is happening is contained in the name, remove it."""
    event.name = (
        event.name.replace(str(event.scheduled_start_time.year), "")
        .replace(" ", " ")
        .strip()
    )
    return event


def main():
    # Load existing events
    events_data_path = HERE.parent / "data" / "events.yaml"
    with open(events_data_path, "r", encoding="utf-8") as f:
        existing_events = yaml.safe_load(f) or {}

    # Fetch, filter and process events from Discord
    discord_events = [remove_year_in_name(e) for e in fetch_from_discord()]
    discord_events = [
        e
        for e in discord_events
        if (
            is_relevant_discord_event(e)
            and not matches_existing_event(e, existing_events)
        )
    ]

    # Add relevant events from Discord
    updated_events = add_events(existing_events, discord_events)

    # Write updated events back to yaml
    with open(events_data_path, "w", encoding="utf-8") as f:
        yaml.dump(updated_events, f, sort_keys=False, allow_unicode=True)

    print("-".join([slugify(e.name) for e in discord_events]), end=None)


if __name__ == "__main__":
    main()
