import logging

from actions import inline_action
from activities.activity import Activity
from activities.silence_state import SilenceState
from event import EventEnum, Event, EVENT_KEY_Q, EVENT_KEY_UP, EVENT_KEY_RIGHT, EVENT_KEY_LEFT, EVENT_BUTTON_PLAY, \
    EVENT_BUTTON_NEXT, EVENT_BUTTON_PREV

class MessageHandler:
    def __init__(self):
        pass

    def expects(self, event_id: EventEnum ) -> bool:
        return False

    def execute(self, context, event: Event) -> bool:
        """
        Return FALSE if we want to quit
        :param context:
        :param event:
        :return:
        """
        return True


class TransitionHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        if event_id == EventEnum.TRANSITION_TO_FIRST:
            return True
        elif event_id == EventEnum.TRANSITION_TO_NEXT:
            return True
        elif event_id == EventEnum.TRANSITION_TO_NAMED:
            return True
        elif event_id == EventEnum.TRANSITION_TO_GIVEN:
            return True
        return False

    def execute(self, context, event: Event) -> bool:
        override_sleep_signal = False
        if hasattr(event, "override_ignorable_events"):
            if event.override_ignorable_events:
                override_sleep_signal = True

        if not context.is_asleep() or override_sleep_signal:
            if event.id == EventEnum.TRANSITION_TO_FIRST:
                self.transition_to_first(context)
            elif event.id == EventEnum.TRANSITION_TO_NEXT:
                self.transition_to_next(context)
            elif event.id == EventEnum.TRANSITION_TO_NAMED:
                self.transition_to_named_state(context, event.data)
            elif event.id == EventEnum.TRANSITION_TO_GIVEN:
                self.transition_to(context, event.target_state)
        return True

    def transition_to_first(self, context):
        """Transition to the first state"""
        context._current_activity_index = 0
        activity = context._activity_objects[context._current_activity_index]
        self.transition_to(context, activity)

    def transition_to_next(self, context):
        """
        transition to next, HOWEVER if the user has say pressed the mode button multiple times
        we may skip modes. this is handled by manipulating the self._state_increment variable
        :return:
        """
        context._current_activity_index += context._activity_increment
        context._current_activity_index = context._current_activity_index % len(context._activity_objects)
        activity = context._activity_objects[context._current_activity_index]
        context._activity_increment = 1
        self.transition_to(context, activity)

    def transition_to(self, context, activity: Activity):
        logging.info("Transitioning to '{}'".format(activity.title))
        context._remove_current_activity()
        context._setup_activity(activity)
        context._current_activity.run()

    def transition_to_named_state(self, context, name):
        if name is None:
            return False
        found = -1
        for index, s in enumerate(self._activity_objects):
            if s.title:
                if s.title.lower() == name.lower():
                    found = index
        if found < 0:
            return False
        context.transition_to(context._activity_objects[found])
        return True


class SilentModeHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        if event_id == EventEnum.ENTER_SLEEP_NOW:
            return True
        elif event_id == EventEnum.ENTER_SLEEP_IF_ABLE:
            return True
        elif event_id == EventEnum.EXIT_SLEEP:
            return True
        return False

    def execute(self, context, event: Event) -> bool:
        if event.id == EventEnum.ENTER_SLEEP_NOW:
            self.go_to_sleep(context,event)
        elif event.id == EventEnum.ENTER_SLEEP_IF_ABLE:
            self.go_to_sleep(context,event)
        elif event.id == EventEnum.EXIT_SLEEP:
            self._notify(context, event)
        return True

    def create_enter_sleep_event(self, context):
        state = SilenceState(context.app_state, {})
        event = Event(EventEnum.TRANSITION_TO_GIVEN)
        event.target_state = state
        context.add_event(event)

    def go_to_sleep(self, context, event):
        # if event is ENTER_SLEEP_NOW, this should pause/stop the activity
        context.notify(event)
        if context.is_no_activity_set() or not context.is_activity_active():
            ev = self.create_enter_sleep_event(context)
            context.add_event(ev)

class IdentityHandler(MessageHandler):
    """
    This handles the ENTER and EXIT events, currently these are only generated
    by the bluetooth handler but there could be other devices
    """
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        if event_id == EventEnum.ENTER_OWNER:
            return True
        elif event_id == EventEnum.EXIT_OWNER:
            return True
        return False

    def execute(self, context, event: Event) -> bool:
        override_sleep_signal = False
        if hasattr(event, "override_ignorable_events"):
            if event.override_ignorable_events:
                override_sleep_signal = True

        if not context.is_asleep() or override_sleep_signal:
            if event.id == EventEnum.ENTER_OWNER:
                self._notify(event)
            elif event.id == EventEnum.EXIT_OWNER:
                self._notify(event)
        return True


class AlarmHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        if event_id == EventEnum.ALARM_INTERRUPT or \
                event_id == EventEnum.ALARM_CONTINUE:
            return True
        return False

    def execute(self, context, event: Event) -> bool:
        """Triggered when context is interrupted"""
        if event.id == EventEnum.ALARM_CONTINUE:
            self.do_alarm_continue(context)
            return True
        if context._current_activity is None:
            # we are probably not even started yet, so ignore
            # any interrupts until we are in a valid state
            return
        logging.debug("interrupting current state")
        context.interrupted_state.append({'state': context._current_activity})
        context.notify(event)
        if event.target_state:
            logging.debug("transitioning to new target state")
            context.add_action(event)
        return True

    def do_alarm_interrupt(self, context, ev):
        """Triggered when context is interrupted"""
        if context._current_activity is None:
            # we are probably not even started yet, so ignore
            # any interrupts until we are in a valid state
            return
        logging.debug("interrupting current state")
        context.interrupted_state.append({'state': context._current_activity})
        if ev is None:
            ev = Event(EventEnum.INTERRUPT)
        context.notify(ev)
        if ev.target_state:
            new_event = Event(EventEnum.TRANSITION_TO_GIVEN)
            new_event.target_state = ev.target_state
            context.add_event(new_event)

    def do_alarm_continue(self, context):
        """Triggered when context is required to continue after interruption"""
        logging.debug("continuing current state")
        if context.is_interrupted():
            previous_state = context.interrupted_state.pop()
            ev = Event(EventEnum.TRANSITION_TO_GIVEN)
            ev.target_state = previous_state["state"]
            context.add_event(ev)

class BluetoothHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        if event_id == EventEnum.BLUETOOTH_EVENT:
            return True
        return False

    def execute(self, context, event: Event) -> bool:
        self._handle_bluetooth_detector(context, event)

    def owner_entered(self, context, who: str, when: float) -> None:
        ev = Event(EventEnum.ENTER_OWNER)
        ev.data = { "when": when, "who": who }
        context.add_event(ev)

    def owner_exited(self, context, who: str, when: float) -> None:
        ev = Event(EventEnum.EXIT_OWNER)
        ev.data = {"when": when, "who": who}
        context.add_event(ev)

    def _handle_bluetooth_detector(self, context, event):
        if not context.config().bluetooth_owners_capability:
            return

        if context.bluetooth_event_fifo is None:
            logging.debug("bluetooth event fifo is not specified")
            return
        if len(event.data) == 0:
            logging.debug("empty event data")
            return
        logging.debug("bluetooth event found '{}'".format(event))
        try:
            (when, why, owner) = event.data.split(",")
            logging.debug("bluetooth event :: when: {} why: {} who:{}".format(when, why, owner))
            if why.upper() == "ENTER":
                self.owner_entered(context, owner, when)
            elif why.upper() == "EXIT":
                self.owner_exited(context, owner, when)
            else:
                logging.debug("unhandled message from bluetooth detector {}".format(event.data))
        except:
            logging.debug("invalid bluetooth event: {}".format(event.data))

class NetworkHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        if event_id == EventEnum.NETWORK_FOUND or \
                event_id == EventEnum.NETWORK_LOST or \
                event_id == EventEnum.INTERNET_FOUND or \
                event_id == EventEnum.INTERNET_LOST:
            return True
        return False

    def execute(self, context, event: Event) -> bool:
        context.notify(event)

class KeyboardHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        return event_id == EventEnum.KEY_PRESS

    def execute(self, context, event: Event) -> bool:
        logging.debug("keyboard event detected")
        if event.data == EVENT_KEY_Q:
            context.stop()
        elif event.data == EVENT_KEY_UP:
            context._current_activity.on_play_down()
        elif event.data == EVENT_KEY_RIGHT:
            context._current_activity.on_next_track_down()
        elif event.data == EVENT_KEY_LEFT:
            context._current_activity.on_previous_track_down()

class SpeakerInputHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        return event_id == EventEnum.BUTTON_DOWN

    def execute(self, context, event: Event) -> bool:
        logging.debug("device event detected")
        if event.data == EVENT_BUTTON_PLAY:
            context._current_activity.on_play_down()
        if event.data == EVENT_BUTTON_NEXT:
            context._current_activity.on_next_track_down()
        if event.data == EVENT_BUTTON_PREV:
            context._current_activity.on_previous_track_down()

class QuitHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        return event_id == EventEnum.QUIT

    def execute(self, context, event: Event) -> bool:
        context.notify(event)
        return False

class ReloadHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def expects(self, event_id: EventEnum) -> bool:
        return event_id == EventEnum.QUIT

    def execute(self, context, event: Event) -> bool:
        context.handle_reload_config(context)
        return False

    def handle_reload_config(self, context):
        """
        Reload everything
        :return:
        """
        raise ValueError("this is wrong")
        inline_action("I am reloading my activities, sorry for the inconvenience.")
        context.app_state.reload()
        new_states = context.personality().get_states()
        c_state_title = context._current_activity.title
        context._activity_objects = new_states
        if c_state_title:
            ev = Event(EventEnum.TRANSITION_TO_NAMED)
            ev.data = c_state_title
        else:
            ev = Event(EventEnum.TRANSITION_TO_FIRST)
        context.add_event(ev)

