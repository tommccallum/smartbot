"""
Pick from a selection of sayings based on factors
could be random or date or time etc

[
{
    "date": ,
    "time_of_day": ,
    "text": "Good morning, %O"
}
]

"""
import random


class SpeechBubble():
    def __init__(self, json:list =None):
        self.json = json

    def all_match(self, criteria ):
        """filter and return a speech bubble"""
        sb = SpeechBubble()
        remainder = []
        for item in self.json:
            matches_all = True
            for cr in criteria:
                if not self._match(item, cr, criteria[cr]):
                    matches_all = False
                    break
            if matches_all:
                remainder.append(item)
        sb.json = remainder
        return sb

    def at_least_one_match(self, criteria ):
        """filter and return a speech bubble"""
        sb = SpeechBubble()
        remainder = []
        for item in self.json:
            for cr in criteria:
                if self._match(item, cr, criteria[cr]):
                    remainder.append(item)
                    break
        sb.json = remainder
        return sb

    def random(self):
        pick = random.choice(self.json)
        return pick["text"]

    def _match(self, item, criteria_type, criteria_value):
        """
        matches if item does not have criteria_type
        :param item:
        :param criteria_type:
        :param criteria_value:
        :return:
        """
        if not criteria_type in item:
            return True
        criteria_type = criteria_type.lower()
        case_insensitive_value = criteria_value.lower()
        case_insensitive_actual = item[criteria_type].lower()
        is_match = False
        if criteria_type == "day_of_week":
            is_match = self._cmp_day_of_week(case_insensitive_actual, case_insensitive_value)
        if criteria_type == "date":
            is_match = self._cmp_date_expr(case_insensitive_value)
        return is_match

    def _cmp_day_of_week(self, case_insensitive_actual, case_insensitive_value):
        possibilities = []
        if case_insensitive_value[0:6] == "weekday":
            possibilities = [case_insensitive_value, "monday", "tuesday", "wednesday", "thursday", "friday"]
        elif case_insensitive_value[0:6] == "weekend":
            possibilities = [case_insensitive_value, "saturday", "sunday"]
        else:
            possibilities = [case_insensitive_value]
        return case_insensitive_actual in possibilities

    def _cmp_date_expr(self, actual, value):
        """
        Check if date between two values
        :param value:
        :return:
        """
        pass

    def _cmp_part_of_day(self, actual, value):
        possibilities = []
        if value == "lunch":
            possibilities = [ "morning", "afternoon", "lunch" ]
        else:
            possibilities = [ value ]
        return actual in possibilities

