"""
A temporary fix for tzwhere, does not follow PEP8 as the rest of the code base.
"""
import collections
import json
from pathlib import Path

import numpy
from tzwhere.tzwhere import feature_collection_polygons, read_tzworld, tzwhere

WRAP = numpy.asarray
COLLECTION_TYPE = numpy.ndarray
__data_path = Path(__file__).parent.parent.joinpath('data')
DEFAULT_POLYGONS = __data_path.joinpath('tz_world.json')
DEFAULT_SHORTCUTS = __data_path.joinpath('tz_world_shortcuts.json')


class TzWhere(tzwhere):
    def __init__(self, forceTZ=True):
        featureCollection = read_tzworld(str(DEFAULT_POLYGONS))
        pgen = feature_collection_polygons(featureCollection)
        self.timezoneNamesToPolygons = collections.defaultdict(list)
        self.unprepTimezoneNamesToPolygons = collections.defaultdict(list)
        for tzname, poly in pgen:
            self.timezoneNamesToPolygons[tzname].append(poly)
        for tzname, polys in self.timezoneNamesToPolygons.items():
            self.timezoneNamesToPolygons[tzname] = WRAP(polys)

            if forceTZ:
                self.unprepTimezoneNamesToPolygons[tzname] = WRAP(polys)

        with open(str(DEFAULT_SHORTCUTS), 'r') as f:
            self.timezoneLongitudeShortcuts, self.timezoneLatitudeShortcuts = json.load(
                f)

        self.forceTZ = forceTZ
        for tzname in self.timezoneNamesToPolygons:
            # Convert things to tuples to save memory
            for degree in self.timezoneLatitudeShortcuts:
                for tzname in self.timezoneLatitudeShortcuts[degree].keys():
                    self.timezoneLatitudeShortcuts[degree][tzname] = \
                        tuple(self.timezoneLatitudeShortcuts[degree][tzname])

            for degree in self.timezoneLongitudeShortcuts.keys():
                for tzname in self.timezoneLongitudeShortcuts[degree].keys():
                    self.timezoneLongitudeShortcuts[degree][tzname] = \
                        tuple(self.timezoneLongitudeShortcuts[degree][tzname])
        try:
            super().__init__(forceTZ)
        except FileNotFoundError:
            pass
