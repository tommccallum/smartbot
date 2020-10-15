import unittest
import os
import sys
from unittest.mock import patch
import datetime
from freezegun import freeze_time

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))

from sleep_mode import SleepMode
from event import Event, EventEnum
import globalvars


from app_state import AppState

class TestSleepMode(unittest.TestCase):
    def create_instance(self):
        test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
        globalvars.app_state = AppState.create_from_file(test_config)
        p = globalvars.app_state.personality
        p.json["sleep"] = {
            "enabled": True,
            "begin": {
                "hard": "09:00",
                "soft": "09:30"
            },
            "end": "11:40",
            "on_end": "Live Radio",
            "phrases": ["Its only %T, go back to sleep Innogen.",
                        "Its not quite morning Innogen, go back to sleep",
                        "Its really early Innogen, go back to sleep"
                        ]
        }
        sm = SleepMode(globalvars.app_state)
        return sm

    def setUp(self) -> None:
        pass

    def test_has_sleep_mode(self):
        sm = self.create_instance()
        self.assertTrue(sm.has_sleep_mode())

    def test_is_sleep_mode_enabled(self):
        sm = self.create_instance()
        self.assertTrue(sm.has_sleep_mode())

    def test_get_hard_sleep_time(self):
        sm = self.create_instance()
        self.assertEqual("09:00", sm.get_hard_sleep_time())

    def test_get_soft_sleep_time(self):
        sm = self.create_instance()
        self.assertEqual("09:30", sm.get_soft_sleep_time())

    def test_get_end_sleep_time(self):
        sm = self.create_instance()
        self.assertEqual("11:40", sm.get_end_sleep_time())

    def test_get_on_end_sleep_time(self):
        sm = self.create_instance()
        self.assertEqual("Live Radio", sm.get_on_end_sleep_action())

    def test_check_sleep_spec_is_valid(self):
        sm = self.create_instance()
        self.assertTrue(sm.check_sleep_spec_is_valid())

    def test_check_sleep_spec_is_valid_missing_hard_time(self):
        sm = self.create_instance()
        saved = sm.json["begin"]["hard"]
        del sm.json["begin"]["hard"]
        self.assertTrue(sm.check_sleep_spec_is_valid)
        sm.json["begin"]["hard"] = saved

    def test_check_sleep_spec_is_invalid_missing_begin(self):
        sm = self.create_instance()
        saved = sm.json["begin"]
        del sm.json["begin"]
        self.assertRaises(ValueError, sm.check_sleep_spec_is_valid)
        sm.json["begin"] = saved

    def test_check_sleep_spec_is_invalid_missing_end_time(self):
        sm = self.create_instance()
        saved = sm.json["end"]
        del sm.json["end"]
        self.assertRaises(ValueError, sm.check_sleep_spec_is_valid)
        sm.json["end"] = saved

    def test_check_sleep_spec_is_invalid_missing_on_end_action(self):
        sm = self.create_instance()
        saved = sm.json["on_end"]
        del sm.json["on_end"]
        self.assertRaises(ValueError, sm.check_sleep_spec_is_valid)
        sm.json["on_end"] = saved

    def test_get_today_as_string(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual("2020-07-03", sm.get_today_as_string())

    def test_get_hard_sleep_as_datetime(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual(datetime.datetime(2020,7,3,9,0,0), sm._get_hard_sleep_as_datetime())

    def test_get_soft_sleep_as_datetime(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual(datetime.datetime(2020,7,3,9,30,0), sm._get_soft_sleep_as_datetime())

    def test_get_earliest_start(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual(datetime.datetime(2020,7,3,9,0,0), sm.get_earliest_start())

    def test_get_latest_start(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 30, 0), sm.get_latest_start())


    def test_get_earliest_start_missing_soft(self):
        sm = self.create_instance()
        del sm.json["begin"]["soft"]
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual(datetime.datetime(2020,7,3,9,0,0), sm.get_earliest_start())
        sm.json["begin"]["soft"] = "09:00"

    def test_get_end_sleep_as_datetime(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            self.assertEqual(datetime.datetime(2020,7,3,11,40,0), sm.get_end_sleep_as_datetime())

    def test_setup_sleep_timings_same_day_set_before_asleep(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 05:00:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,3,11,40,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_same_day_set_after_waking(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 11:41:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 4, 9, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 4, 9, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,4,11,40,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_same_day_set_while_asleep(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 10:41:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,3,11,40,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_same_day_set_equal_to_waking(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 11:40:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 9, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,3,11,40,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_same_day_set_equal_to_waking_after(self):
        sm = self.create_instance()
        with freeze_time("2020-07-03 11:41:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7,4, 9, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 4, 9, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,4,11,40,0), sm.end_sleep_datetime)


    def test_setup_sleep_timings_next_day_set_before_asleep(self):
        sm = self.create_instance()
        sm.json["begin"] = { "soft": "21:00", "hard":"21:30" }
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 09:00:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,4,8,0,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_next_day_set_after_waking(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] ="08:00"
        with freeze_time("2020-07-03 08:01:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,4,8,0,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_next_day_set_while_asleep(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 23:41:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,4,8,0,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_next_day_set_while_asleep_early_am(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 02:41:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 2, 21, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 2, 21, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,3,8,0,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_next_day_set_equal_to_wakeup_early_am(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 08:00:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 2, 21, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 2, 21, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,3,8,0,0), sm.end_sleep_datetime)

    def test_setup_sleep_timings_next_day_set_equal_to_wakeup_after(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 08:01:00"):
            sm.setup_sleep_timings()
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 0, 0), sm.soft_sleep_datetime)
            self.assertEqual(datetime.datetime(2020, 7, 3, 21, 30, 0), sm.hard_sleep_datetime)
            self.assertEqual(datetime.datetime(2020,7,4,8,0,0), sm.end_sleep_datetime)


    def test_is_ready_to_wake_up_is_true(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 08:00:00"):
            sm.setup_sleep_timings()
            self.assertTrue(sm.is_ready_to_wake_up())

    def test_is_ready_to_wake_up_too_early_on_same_day(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 07:59:00"):
            sm.setup_sleep_timings()
            self.assertFalse(sm.is_ready_to_wake_up())

    def test_is_ready_to_wake_up_too_early_on_day_before(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 23:59:00"):
            sm.setup_sleep_timings()
            self.assertFalse(sm.is_ready_to_wake_up())

    def test_is_ready_to_wake_up_after(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 08:01:00"):
            sm.setup_sleep_timings()
            self.assertFalse(sm.is_ready_to_wake_up())

    def test_is_ready_to_sleep_at_soft(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 21:00:00"):
            sm.setup_sleep_timings()
            result = sm.is_ready_to_sleep()
            self.assertEqual(result.id, EventEnum.ENTER_SLEEP_IF_ABLE)

    def test_is_ready_to_sleep_after_soft(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 21:15:00"):
            sm.setup_sleep_timings()
            result = sm.is_ready_to_sleep()
            self.assertEqual(result.id, EventEnum.ENTER_SLEEP_IF_ABLE)

    def test_is_ready_to_sleep_at_hard(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 21:30:00"):
            sm.setup_sleep_timings()
            result = sm.is_ready_to_sleep()
            self.assertEqual(result.id, EventEnum.ENTER_SLEEP_NOW)

    def test_is_ready_to_sleep_after_hard(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 21:31:00"):
            sm.setup_sleep_timings()
            result = sm.is_ready_to_sleep()
            self.assertEqual(result.id, EventEnum.ENTER_SLEEP_NOW)

    def test_is_ready_to_sleep_after_end(self):
        sm = self.create_instance()
        sm.json["begin"] = {"soft": "21:00", "hard": "21:30"}
        sm.json["end"] = "08:00"
        with freeze_time("2020-07-03 08:00:00"):
            sm.setup_sleep_timings()
            self.assertFalse(sm.is_ready_to_sleep())

if __name__ == '__main__':
    unittest.main()
