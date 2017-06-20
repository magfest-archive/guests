import pytest

from bands import *


class TestBandProperties:
    def test_normalized_group_name(self):
        group = Group(name="$Test's Cool Band &     Friends#%@", band=Band())
        assert group.band.normalized_group_name == "tests_cool_band_friends"
