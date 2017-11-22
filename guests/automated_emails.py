from guests import *

AutomatedEmail.queries[GuestGroup] = lambda session: session.query(GuestGroup).options(joinedload(GuestGroup.group)).all()


class BandEmail(AutomatedEmail):
    def __init__(self, subject, template, filter, ident, **kwargs):
        AutomatedEmail.__init__(self, GuestGroup, subject, template, lambda b: b.group_type == c.BAND and filter(b),
                                ident, sender=c.BAND_EMAIL, **kwargs)


class GuestEmail(AutomatedEmail):
    def __init__(self, subject, template, filter, ident, **kwargs):
        AutomatedEmail.__init__(self, GuestGroup, subject, template, lambda b: b.group_type == c.GUEST and filter(b),
                                ident, sender=c.GUEST_EMAIL, **kwargs)

AutomatedEmail(GuestGroup, '{EVENT_NAME} Performer Checklist', 'band_notification.txt',
               lambda b: b.group_type == c.BAND, sender=c.BAND_EMAIL,
               ident='band_checklist_inquiry')

BandEmail('Last chance to apply for a {EVENT_NAME} Panel', 'band_panel_reminder.txt',
          lambda b: not b.panel_status, when=days_before(3, c.BAND_PANEL_DEADLINE),
          ident='band_panel_reminder')

BandEmail('Last Chance to accept your offer to perform at {EVENT_NAME}', 'band_agreement_reminder.txt',
          lambda b: not b.info_status, when=days_before(3, c.BAND_INFO_DEADLINE),
          ident='band_agreement_reminder')

BandEmail('Last chance to include your bio info on the {EVENT_NAME} website', 'band_bio_reminder.txt',
          lambda b: not b.bio_status, when=days_before(3, c.BAND_BIO_DEADLINE),
          ident='band_bio_reminder')

BandEmail('{EVENT_NAME} W9 reminder', 'band_w9_reminder.txt',
          lambda b: b.payment and not b.taxes_status, when=days_before(3, c.BAND_TAXES_DEADLINE),
          ident='band_w9_reminder')

BandEmail('Last chance to sign up for selling merchandise at {EVENT_NAME}', 'band_merch_reminder.txt',
          lambda b: not b.merch_status, when=days_before(3, c.BAND_MERCH_DEADLINE),
          ident='band_merch_reminder')

BandEmail('{EVENT_NAME} charity auction reminder', 'band_charity_reminder.txt',
          lambda b: not b.charity_status, when=days_before(3, c.BAND_CHARITY_DEADLINE),
          ident='band_charity_reminder')

BandEmail('{EVENT_NAME} stage plot reminder', 'band_stage_plot_reminder.txt',
          lambda b: not b.stage_plot_status, when=days_before(3, c.BAND_STAGE_PLOT_DEADLINE),
          ident='band_stage_plot_reminder')

AutomatedEmail(GuestGroup, 'It\'s time to send us your info for {EVENT_NAME}!', 'guest_checklist_announce.html',
               lambda g: g.group_type == c.GUEST, ident='guest_checklist_inquiry', sender=c.GUEST_EMAIL)

GuestEmail('Reminder: Please complete your Guest Checklist for {EVENT_NAME}!',
           'guest_checklist_reminder.html',
           lambda g: not g.checklist_completed,
           when=days_before(7, c.GUEST_BIO_DEADLINE - timedelta(days=7)),
           ident='guest_reminder_1')

GuestEmail('Have you forgotten anything? Your {EVENT_NAME} Guest Checklist needs you!',
           'guest_checklist_reminder.html',
           lambda g: not g.checklist_completed,
           when=days_before(7, c.GUEST_BIO_DEADLINE),
           ident='guest_reminder_2')
