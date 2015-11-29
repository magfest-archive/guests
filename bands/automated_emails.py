from bands import *

AutomatedEmail.extra_models[Band] = lambda session: session.query(Band).options(joinedload(Band.group)).all()

AutomatedEmail(Band, '{EVENT_NAME} Performer Checklist', 'band_notification.txt',
               lambda band: True, sender=c.BAND_EMAIL)
