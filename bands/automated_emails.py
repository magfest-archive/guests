from bands import *

AutomatedEmail.queries[Band] = lambda session: session.query(Band).options(joinedload(Band.group)).all()


class BandEmail(AutomatedEmail):
    def __init__(self, subject, template, filter, ident, **kwargs):
        AutomatedEmail.__init__(self, Band, subject, template, lambda b: b.group_type == c.BAND and filter(b), ident, sender=c.BAND_EMAIL, **kwargs)

AutomatedEmail(Band, '{EVENT_NAME} Performer Checklist', 'band_notification.txt', lambda b: b.group_type == c.BAND,
               ident='band_checklist_inquiry')

BandEmail('Last chance to apply for a {EVENT_NAME} Panel', 'band_panel_reminder.txt',
          lambda b: not b.status('panel'), when=days_before(3, c.BAND_PANEL_DEADLINE),
          ident='band_panel_reminder')

BandEmail('Last Chance to accept your offer to perform at {EVENT_NAME}', 'band_agreement_reminder.txt',
          lambda b: not b.status('info'), when=days_before(3, c.BAND_INFO_DEADLINE),
          ident='band_agreement_reminder')

BandEmail('Last chance to include your bio info on the {EVENT_NAME} website', 'band_bio_reminder.txt',
          lambda b: not b.status('bio'), when=days_before(3, c.BAND_BIO_DEADLINE),
          ident='band_bio_reminder')

BandEmail('{EVENT_NAME} W9 reminder', 'band_w9_reminder.txt',
          lambda b: b.payment and not b.status('taxes'), when=days_before(3, c.BAND_TAXES_DEADLINE),
          ident='band_w9_reminder')

BandEmail('Last chance to sign up for selling merchandise at {EVENT_NAME}', 'band_merch_reminder.txt',
          lambda b: not b.status('merch'), when=days_before(3, c.BAND_MERCH_DEADLINE),
          ident='band_merch_reminder')

BandEmail('{EVENT_NAME} charity auction reminder', 'band_charity_reminder.txt',
          lambda b: not b.status('charity'), when=days_before(3, c.BAND_CHARITY_DEADLINE),
          ident='band_charity_reminder')

BandEmail('{EVENT_NAME} stage plot reminder', 'band_stage_plot_reminder.txt',
          lambda b: not b.status('stage_plot'), when=days_before(3, c.BAND_STAGE_PLOT_DEADLINE),
          ident='band_stage_plot_reminder')
