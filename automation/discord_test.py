from datetime import datetime

from discord import matches_existing_event, is_relevant_discord_event, ScheduledEvent

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
