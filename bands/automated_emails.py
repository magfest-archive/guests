from bands import *

AutomatedEmail.extra_models[Band] = lambda session: session.query(Band).options(joinedload(Band.group)).all()

# TODO: fill this in with whatever we need, like if we should email them right away or what
AutomatedEmail(Band, 'Band Example Email Subject', 'band_notification.txt',
               lambda b: True, sender=c.BAND_EMAIL)
