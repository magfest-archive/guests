from bands import *

AutomatedEmail.queries[Band] = lambda session: session.query(Band).options(joinedload(Band.group)).all()


# TODO: test to make sure this still works
# it's doing stuff with len(args) here and we changed the length to include date_filter
class BandEmail(AutomatedEmail):
    def __init__(self, *args, **kwargs):
        if len(args) < 3 and 'filter' not in kwargs:
            kwargs['filter'] = lambda x: True
        AutomatedEmail.__init__(self, Band, *args, sender=c.BAND_EMAIL, **kwargs)

BandEmail('{EVENT_NAME} Performer Checklist', 'band_notification.txt')

BandEmail('Last chance to apply for a {EVENT_NAME} Panel', 'band_panel_reminder.txt',
          lambda b: not b.completed('panel'), date_filters=days_before(3, c.BAND_PANEL_DEADLINE))

BandEmail('Last Chance to accept your offer to perform at {EVENT_NAME}', 'band_agreement_reminder.txt',
          lambda b: not b.completed('info'), date_filters=days_before(3, c.BAND_AGREEMENT_DEADLINE))

BandEmail('Last chance to include your bio info on the {EVENT_NAME} website', 'band_bio_reminder.txt',
          lambda b: not b.completed('bio'), date_filters=days_before(3, c.BAND_BIO_DEADLINE))

BandEmail('{EVENT_NAME} W9 reminder', 'band_w9_reminder.txt',
          lambda b: b.payment and not b.completed('taxes'), date_filters=days_before(3, c.BAND_W9_DEADLINE))

BandEmail('Last chance to sign up for selling merchandise at {EVENT_NAME}', 'band_merch_reminder.txt',
          lambda b: not b.completed('merch'), date_filters=days_before(3, c.BAND_MERCH_DEADLINE))

BandEmail('{EVENT_NAME} charity auction reminder', 'band_charity_reminder.txt',
          lambda b: not b.completed('charity'), date_filters=days_before(3, c.BAND_CHARITY_DEADLINE))

BandEmail('{EVENT_NAME} stage plot reminder', 'band_stage_plot_reminder.txt',
          lambda b: not b.completed('stage_plot'), date_filters=days_before(3, c.STAGE_AGREEMENT_DEADLINE))
