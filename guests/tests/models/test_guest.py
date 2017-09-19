import pytest

from guests import *


class TestGuestProperties:
    def test_normalized_group_name(self):
        group = Group(name="$Test's Cool Band &     Friends#%@", guest=GuestGroup())
        assert group.guest.normalized_group_name == "tests_cool_band_friends"
