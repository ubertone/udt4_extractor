# -*- coding: UTF_8 -*-

# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer, Damien Dufour

from math import fmod
from datetime import datetime


# TODO: ajouter une méthode qui retourne la date sous forme de YYYY.MM.DD HH.MM.SS.xxx ?

class ub_time_t():
    """
    @brief class to handle the time reference used in the data (sec, n_sec) whithout loose of precision.
    _n_sec is forced to be in ]1e9, -1e9[, if _n_sec is over that limit, the excedent is added to _sec
    Over all precision: -/+ 1ns
    Can interact with objects from ub_time_t, int, float, list (len=2), tuples (len=2)
    """

    @staticmethod
    def _process_nsec(_nsecs):
        """
        @brief Force nsecs to be between ]1s, -1s[, return the exedent of secs and the remaining nsecs.
        Return both, seconds and nsecs as integers.

        @param _nsecs (int) number of nano seconds
        @return int Excedent of seconds from _nsecs
        @return int Remaining of nano seconds from _nsecs (1s> nano secs >-1s)
        """
        res_nsec = fmod(_nsecs, 1e9)
        diff_sec = (_nsecs - res_nsec) / 1e9
        return int(diff_sec), int(res_nsec)

    @staticmethod
    def _process_fsec(_fsec):
        """
        @brief Transform a float respresenting a time as seconds, separates secs and nsecs.
        Return the seconds as int, the nanosecs are still floats, expressed as nanoseconds.

        @param _fsec (float) Number of seconds, decimal values is added to nanoseconds
        @return int Remaining of seconds from _fsec
        @return float Excedent of nano seconds from _fsec (1s> nano secs >-1s)
        """
        decimal = fmod(_fsec, 1.0)
        integer = int(_fsec - decimal)
        return integer, decimal * 1e9

    def __init__(self, _sec=0, _n_sec=0):
        """
        @brief Build ub_time_t object, rearrange the given values as 2 intergers sec and nsec.
        1st, the decimal part of nsecs is added to nsecs, the integer part of secs is returned as an int
        2nd, the excedent nsecs from secs is added to the given nsecs.
        If nsecs >1s (or <-1s) the excedent of secs is separated and returned as int, the remainnig nsecs are returned as int.
        3rd, the excess of secs from nsecs is added to the secs extracted in 1st step.
        4th, sec and nsec are forced to be both, either positive or negative. Except when secs=0, nsecs can be negative.

        @param _sec (float, int) Number of seconds. Decimal values is added to nanoseconds (for float)
        @param _n_sec (forced as int) Number of nano seconds.
        """
        new_secs, add_nsecs = self._process_fsec(_sec)
        add_secs, self.nsec = self._process_nsec(_n_sec + add_nsecs)
        self.sec = new_secs + add_secs
        self._simplify_data()

    def _simplify_data(self):
        """
        @brief Force sec and nsec to be either both positive or negative. Except when sec=0, nsec can be negative.
        simplifies the saved data:
        sec = 2, nsec = -123456789 => sec=1, nsec=876543211
        sec = -2, nsec = 123456789 => sec=-1, nsec=-876543211
        sec = -1, nsec = 500000000 => sec=0, nsec=-500000000
        """
        # makes sec and nsec both positives
        if self.sec > 0 and self.nsec < 0:
            self.sec -= 1
            self.nsec += 1000000000
        # makes sec and nsec both negatives
        if self.sec < 0 and self.nsec > 0:
            self.sec += 1
            self.nsec -= 1000000000

    def as_float(self):
        """
        @brief Return the result as a float (expressed in seconds).
        Result may not be accurate if sec is large (>10⁷ with double)

        @return float Stored data expressed as float
        """
        return self.sec + 1e-9 * self.nsec

    def diff_as_float(self, other):
        """
        @brief Return the difference of "self - other" as a float (expressed in seconds).

        @param other (any valid object) Some other time reference (int, float, list, tuple, ub_time_t)
        @return float Difference "self-other" expressed as float
        """
        diff_tr = self.__sub__(other)
        return diff_tr.as_float()

    def as_timestring(self):
        """
        @brief Return the timestamp as a string (expressed as "%d/%m/%Y\t%H:%M:%S.%f").

        @return string expressed as "%d/%m/%Y\t%H:%M:%S.%f")
        """
        return (datetime.utcfromtimestamp(self.as_float()).strftime("%d/%m/%Y\t%H:%M:%S.%f"))

    def as_datetime(self):
        """
        @brief Return the timestamp as a datetime object.

        @return datetime
        """
        return (datetime.utcfromtimestamp(self.as_float()))

    def deepcopy(self):
        """
        @brief return a deepcopy of the object
        @return ub_time_t Copy of self
        """
        return ub_time_t(self.sec, self.nsec)

    def __str__(self):
        """
        @brief Overload of the string representation as "-/+sec.nsec"
        @return string Representation of sec and nsec
        """
        if self.nsec < 0 and self.sec == 0:
            return "-%d.%09d" % (self.sec, -self.nsec)
        elif self.nsec < 0 and self.sec < 0:
            return "%d.%09d" % (self.sec, -self.nsec)
        else:
            return "%d.%09d" % (self.sec, self.nsec)

    # user may compare it with None or sth else, but better use "is" to do so:
    def __eq__(self, other):
        if isinstance(other, (list, tuple, int, float, ub_time_t)):
            return self.diff_as_float(other) == 0.
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, (list, tuple, int, float, ub_time_t)):
            return self.diff_as_float(other) != 0.
        else:
            return True

    def __lt__(self, other):
        return self.diff_as_float(other) < 0.

    def __le__(self, other):
        return self.diff_as_float(other) <= 0.

    def __gt__(self, other):
        return self.diff_as_float(other) > 0.

    def __ge__(self, other):
        return self.diff_as_float(other) >= 0.

    def __neg__(self):
        return ub_time_t(-self.sec, -self.nsec)

    def __rsub__(self, other):
        neg_self = self.__neg__()
        return neg_self.__iadd__(other)

    def __sub__(self, other):
        if isinstance(other, (list, tuple)):
            if len(other) == 2:
                return self.__add__([-other[0], -other[1]])
            else:
                raise
        elif isinstance(other, (int, float, ub_time_t)):
            return self.__add__(-other)
        else:
            raise

    def __isub__(self, other):
        if isinstance(other, (list, tuple)):
            if len(other) == 2:
                return self.__iadd__([-other[0], -other[1]])
            else:
                raise
        elif isinstance(other, (int, float, ub_time_t)):
            return self.__iadd__(-other)
        else:
            raise

    def __radd__(self, other):
        return self.__add__(other)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return ub_time_t(self.sec + other, self.nsec)
        elif isinstance(other, (list, tuple)):
            if len(other) == 2:
                return ub_time_t(self.sec + other[0], self.nsec + other[1])
            else:
                raise
        elif isinstance(other, ub_time_t):
            return ub_time_t(self.sec + other.sec, self.nsec + other.nsec)
        else:
            raise

    def __iadd__(self, other):
        if isinstance(other, (int, float)):
            new_secs, add_nsecs = self._process_fsec(other)
            add_secs, self.nsec = self._process_nsec(self.nsec + add_nsecs)
            self.sec += (new_secs + add_secs)
            self._simplify_data()
            return self
        elif isinstance(other, (list, tuple)):
            if len(other) == 2:
                new_secs, add_nsecs = self._process_fsec(other[0])
                add_secs, self.nsec = self._process_nsec(self.nsec + add_nsecs + other[1])
                self.sec += (new_secs + add_secs)
                self._simplify_data()
                return self
            else:
                raise
        elif isinstance(other, ub_time_t):
            add_secs, self.nsec = self._process_nsec(self.nsec + other.nsec)
            self.sec += (other.sec + add_secs)
            self._simplify_data()
            return self
        else:
            raise
