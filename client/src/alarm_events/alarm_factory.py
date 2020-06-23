from alarm_events.play_alarm_event import PlayAlarmEvent


def create_alarm_event(alarm_action: str, data: object, config: "Configuration"):
    if alarm_action == "play":
        return PlayAlarmEvent(data, config)
    raise Exception("{} is not an alarm event type".format(alarm_action))
