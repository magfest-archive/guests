from bands import *

AutomatedEmail.queries[Band] = lambda session: session.query(Band).options(joinedload(Band.group)).all()


# TODO: test to make sure this still works
# it's doing stuff with len(args) here and we changed the length to include date_filter
class BandEmail(AutomatedEmail):
    def __init__(self, *args, **kwargs):
        if len(args) < 3 and 'filter' not in kwargs:
            kwargs['filter'] = lambda x: True
        AutomatedEmail.__init__(self, Band, *args, sender=c.BAND_EMAIL, **kwargs)

BandEmail('{EVENT_NAME} Performer Checklist', 'band_notification.txt', ident='band_checklist_inquiry')

BandEmail('Last chance to apply for a {EVENT_NAME} Panel', 'band_panel_reminder.txt',
          lambda b: not b.status('panel'), when=days_before(3, c.BAND_PANEL_DEADLINE),
          ident='band_panel_reminder')

BandEmail('Last Chance to accept your offer to perform at {EVENT_NAME}', 'band_agreement_reminder.txt',
          lambda b: not b.status('info'), when=days_before(3, c.BAND_AGREEMENT_DEADLINE),
          ident='band_agreement_reminder')

BandEmail('Last chance to include your bio info on the {EVENT_NAME} website', 'band_bio_reminder.txt',
          lambda b: not b.status('bio'), when=days_before(3, c.BAND_BIO_DEADLINE),
          ident='band_bio_reminder')

BandEmail('{EVENT_NAME} W9 reminder', 'band_w9_reminder.txt',
          lambda b: b.payment and not b.status('taxes'), when=days_before(3, c.BAND_W9_DEADLINE),
          ident='band_w9_reminder')

BandEmail('Last chance to sign up for selling merchandise at {EVENT_NAME}', 'band_merch_reminder.txt',
          lambda b: not b.status('merch'), when=days_before(3, c.BAND_MERCH_DEADLINE),
          ident='band_merch_reminder')

BandEmail('{EVENT_NAME} charity auction reminder', 'band_charity_reminder.txt',
          lambda b: not b.status('charity'), when=days_before(3, c.BAND_CHARITY_DEADLINE),
          ident='band_charity_reminder')

BandEmail('{EVENT_NAME} stage plot reminder', 'band_stage_plot_reminder.txt',
          lambda b: not b.status('stage_plot'), when=days_before(3, c.STAGE_AGREEMENT_DEADLINE),
          ident='band_stage_plot_reminder')
