from bands import *

bands_config = parse_config(__file__)
c.include_plugin_config(bands_config)

# Add the access levels we defined to c.ACCESS* (this will go away if/when we implement enum merging)
c.ACCESS.update(c.BAND_ACCESS_LEVELS)
c.ACCESS_OPTS.extend(c.BAND_ACCESS_LEVEL_OPTS)
c.ACCESS_VARS.extend(c.BAND_ACCESS_LEVEL_VARS)
