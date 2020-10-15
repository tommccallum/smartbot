import logging

from activities.activity import Activity
from activities.end_state import EndState
from activities.facts_state import FactsState
from activities.introduction_state import IntroductionState
from activities.playlist_stream_state import PlaylistStreamState
from activities.speaking_clock import SpeakingClockState

end_state_config = { "title": "end_state", "type": "__end_state" }

def create_activities(app_state) -> list:
    """
        Creates the set of user functionality that has been configured in personality.states
        Each 'State' is passed its own configuration from the file, this is called the state_configuration.
        It also needs the main configuration and personality profile.
    """
    activity_specs = app_state.personality.get_states()
    activity_objects = []
    if len(activity_specs) == 0:
        raise ValueError("No activities found.")
    for activity_spec in activity_specs:
        this_object = create_activity(activity_spec, app_state)
        activity_objects.append(this_object)
    end_state_object = create_activity(end_state_config, app_state)
    activity_objects.append(end_state_object)
    return activity_objects


def create_activity(activity : dict , app_state ) -> Activity:
    try:
        if not "type" in activity:
            raise ValueError("activity missing required 'type' key")
        activity_type = activity["type"].lower()
        if not "title" in activity:
            activity["title"] = activity_type

        logging.info("Creating new '{}' activity with title '{}'".format(activity_type, activity["title"]))
        if activity_type.lower() == "audio":
            return PlaylistStreamState(app_state, activity)
        elif activity_type.lower() == "introduction":
            return IntroductionState(app_state, activity)
        elif activity_type.lower() == "speakingclock":
            return SpeakingClockState(app_state, activity)
        elif activity_type.lower() == "facts":
            return FactsState(app_state, activity)
        elif activity_type.lower() == "__end_state":
            return EndState(app_state, activity)
        else:
            raise ValueError("invalid activity type '{}' specified".format(activity_type))
    except ValueError as err:
        logging.error(err)