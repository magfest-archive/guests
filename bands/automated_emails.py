from bands import *

AutomatedEmail.extra_models[Band] = lambda session: session.query(Band).options(joinedload(Band.group)).all()


class BandEmail(AutomatedEmail):
    def __init__(self, *args, **kwargs):
        if len(args) < 3 and 'filter' not in kwargs:
            kwargs['filter'] = lambda x: True
        AutomatedEmail.__init__(self, Band, *args, sender=c.BAND_EMAIL, **kwargs)

BandEmail('{EVENT_NAME} Performer Checklist', 'band_notification.txt')

BandEmail('Last chance to apply for a {EVENT_NAME} Panel', 'band_panel_reminder.txt',
          lambda b: not b.panel.completed and days_before(3, c.BAND_PANEL_DEADLINE))

BandEmail('Last Chance to accept your offer to perform at {EVENT_NAME}', 'band_agreement_reminder.txt',
          lambda b: not b.info.completed and days_before(3, c.BAND_AGREEMENT_DEADLINE))

BandEmail('Last chance to include your bio info on the {EVENT_NAME} website', 'band_bio_reminder.txt',
          lambda b: not b.bio.completed and days_before(3, c.BAND_BIO_DEADLINE))

BandEmail('{EVENT_NAME} W9 reminder', 'band_w9_reminder.txt',
          lambda b: b.payment and not b.taxes.completed and days_before(3, c.BAND_W9_DEADLINE))

BandEmail('Last chance to sign up for selling merchandise at {EVENT_NAME}', 'band_merch_reminder.txt',
          lambda b: not b.merch.completed and days_before(3, c.BAND_MERCH_DEADLINE))

BandEmail('{EVENT_NAME} charity auction reminder', 'band_charity_reminder.txt',
          lambda b: not b.charity.completed and days_before(3, c.BAND_CHARITY_DEADLINE))

BandEmail('{EVENT_NAME} stage plot reminder', 'band_stage_plot_reminder.txt',
          lambda b: not b.stage_plot.uploaded_file and days_before(3, c.STAGE_AGREEMENT_DEADLINE))
