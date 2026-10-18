from datetime import datetime

from discord import (
    ScheduledEvent,
    is_relevant_discord_event,
    load_events,
    matches_existing_event,
    write_events,
)

RELEVANT_SCHEDULED_EVENT_KWARGS = dict(
    id="1",
    guild_id="1",
    name="NewDance",
    description="Description with any event URL https://fusion-dancing.eu",
    scheduled_start_time=datetime(3021, 1, 1),
    scheduled_end_time=datetime(3021, 2, 2),
    status=1,
    entity_type=3,
    privacy_level=2,
)


def test_link_extraction_from_event():
    assert (
        ScheduledEvent(**RELEVANT_SCHEDULED_EVENT_KWARGS).links[0]
        == "https://fusion-dancing.eu"
    )


def test_is_relevant_discord_event():

    assert is_relevant_discord_event(
        ScheduledEvent(**RELEVANT_SCHEDULED_EVENT_KWARGS)
    ), "Future scheduled external event should be relevant"

    assert not is_relevant_discord_event(
        ScheduledEvent(
            **{
                **RELEVANT_SCHEDULED_EVENT_KWARGS,
                "status": 3,
            }
        )
    ), "Completed event should be irrelevant"

    assert not is_relevant_discord_event(
        ScheduledEvent(
            **{
                **RELEVANT_SCHEDULED_EVENT_KWARGS,
                "scheduled_start_time": datetime(1999, 1, 1),
            }
        )
    ), "Old event should be irrelevant"

    assert not is_relevant_discord_event(
        ScheduledEvent(
            **{
                **RELEVANT_SCHEDULED_EVENT_KWARGS,
                "description": "Does not contain a link.",
            }
        )
    ), "Missing link in description should mark irrelevant"


def test_add_events():
    existing = {
        2020: [{"name": "UnicornDance"}, {"name": "BearDance"}],
        3030: [{"name": "UnicornDance"}],
    }

    assert not matches_existing_event(
        ScheduledEvent(
            id="1",
            guild_id="1",
            name="NewDance",
            scheduled_start_time=datetime(3030, 1, 1),
            scheduled_end_time=datetime(3030, 2, 2),
            status=1,
            entity_type=3,
            privacy_level=2,
        ),
        existing,
    ), "It's an entirely new dance"

    assert matches_existing_event(
        ScheduledEvent(
            id="1",
            guild_id="1",
            name="BearDance",
            scheduled_start_time=datetime(2020, 1, 1),
            scheduled_end_time=datetime(2020, 2, 2),
            status=1,
            entity_type=3,
            privacy_level=2,
        ),
        existing,
    ), "It happened in 2020 and we know"

    assert not matches_existing_event(
        ScheduledEvent(
            id="1",
            guild_id="1",
            name="BearDance",
            scheduled_start_time=datetime(3030, 1, 1),
            scheduled_end_time=datetime(3030, 2, 2),
            status=1,
            entity_type=3,
            privacy_level=2,
        ),
        existing,
    ), "It happened in 2020 but not yet in 3030"


def test_load_and_write_events(tmp_path):
    (tmp_path / "2020.yaml").write_text(
        "- name: UnicornDance\n  start: 2020-01-01\n", encoding="utf-8"
    )
    (tmp_path / "3030.yaml").write_text(
        "- name: BearDance\n  start: 3030-01-01\n", encoding="utf-8"
    )
    # Must be ignored, only year files hold events
    (tmp_path / "scenes.yaml").write_text("- name: Somewhere\n", encoding="utf-8")

    events = load_events(tmp_path)

    assert set(events) == {2020, 3030}, "Years are read from the file names as ints"
    assert events[2020][0]["name"] == "UnicornDance"

    untouched_before = (tmp_path / "2020.yaml").read_text(encoding="utf-8")
    events[3030].append({"name": "NewDance"})
    write_events(tmp_path, events, [3030])

    assert (tmp_path / "2020.yaml").read_text(
        encoding="utf-8"
    ) == untouched_before, "Unchanged years stay untouched"
    assert [e["name"] for e in load_events(tmp_path)[3030]] == [
        "BearDance",
        "NewDance",
    ], "The changed year was written back"


def test_write_events_creates_missing_year(tmp_path):
    write_events(tmp_path, {2031: [{"name": "NewDance"}]}, [2031])

    assert load_events(tmp_path) == {2031: [{"name": "NewDance"}]}
