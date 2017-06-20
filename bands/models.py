from bands import *


def extension(filename):
    return filename.split('.')[-1].lower()


@Session.model_mixin
class Group:
    band = relationship('Band', backref='group', uselist=False)


@Session.model_mixin
class Attendee:
    @property
    def band(self):
        """
        :return: The Band this attendee is part of (either as a performer or a +1 comp), or None if not
        """
        return self.group and self.group.band


@Session.model_mixin
class Event:
    band = relationship('Band', backref='event')


class Band(MagModel):
    group_id = Column(UUID, ForeignKey('group.id'))
    event_id = Column(UUID, ForeignKey('event.id'), nullable=True)
    info = relationship('BandInfo', backref=backref('band', load_on_pending=True), uselist=False)
    bio = relationship('BandBio', backref=backref('band', load_on_pending=True), uselist=False)
    taxes = relationship('BandTaxes', backref=backref('band', load_on_pending=True), uselist=False)
    stage_plot = relationship('BandStagePlot', backref=backref('band', load_on_pending=True), uselist=False)
    panel = relationship('BandPanel', backref=backref('band', load_on_pending=True), uselist=False)
    merch = relationship('BandMerch', backref=backref('band', load_on_pending=True), uselist=False)
    charity = relationship('BandCharity', backref=backref('band', load_on_pending=True), uselist=False)

    payment = Column(Integer, default=0, admin_only=True)
    vehicles = Column(Integer, default=1, admin_only=True)
    estimated_loadin_minutes = Column(Integer, default=c.DEFAULT_LOADIN_MINUTES, admin_only=True)
    estimated_performance_minutes = Column(Integer, default=c.DEFAULT_PERFORMANCE_MINUTES, admin_only=True)

    @property
    def all_badges_claimed(self):
        return not any(a.is_unassigned for a in self.group.attendees)

    @property
    def estimated_performer_count(self):
        return len([a for a in self.group.attendees if a.badge_type == c.GUEST_BADGE]) or 0

    @property
    def performance_minutes(self):
        return self.estimated_performance_minutes

    @property
    def email(self):
        return self.group.email

    @property
    def normalized_group_name(self):
        # Remove all special characters, then remove all extra whitespace, then replace spaces with underscores
        return ' '.join(
            ''.join(e for e in self.group.name.strip().lower() if e.isalnum() or e == ' ').split()
        ).replace(' ', '_')

    def status(self, model):
        """
        This is a safe way to check if a step has been completed and what its status is for a particular band.
        It checks for a custom 'status' property for the step; if that doesn't exist, it will attempt to return
        "Completed" if an ID of the step exists.

        :param model: This should match one of the relationship columns in the Band class, e.g., 'bio' or 'stage_plot'
        :return: Returns either the 'status' property of the model, "Completed," or None.
        """

        subclass = getattr(self, model)
        return getattr(subclass, 'status', getattr(subclass, 'id')) if subclass else None


class BandInfo(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    poc_phone = Column(UnicodeText)
    performer_count = Column(Integer, default=0)
    bringing_vehicle = Column(Boolean, default=False)
    vehicle_info = Column(UnicodeText)
    arrival_time = Column(UnicodeText)

    @property
    def status(self):
        return "Yes" if self.poc_phone else ""


class BandBio(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    desc = Column(UnicodeText)
    website = Column(UnicodeText)
    facebook = Column(UnicodeText)
    twitter = Column(UnicodeText)
    other_social_media = Column(UnicodeText)

    pic_filename = Column(UnicodeText)
    pic_content_type = Column(UnicodeText)

    @property
    def pic_url(self):
        return '../bands/view_bio_pic?id={}'.format(self.band.id) if self.uploaded_pic else ''

    @property
    def pic_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'bio_pics', self.id)

    @property
    def uploaded_pic(self):
        return os.path.exists(self.pic_fpath)

    @property
    def pic_extension(self):
        return extension(self.pic_filename)

    @property
    def download_filename(self):
        return self.band.normalized_group_name + "_bio_pic." + self.pic_extension

    @property
    def status(self):
        return "Yes" if self.desc else ""


class BandTaxes(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    w9_filename = Column(UnicodeText)
    w9_content_type = Column(UnicodeText)

    @property
    def w9_url(self):
        return '../bands/view_w9?id={}'.format(self.band.id) if self.w9_filename else ''

    @property
    def w9_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'w9_forms', self.id)

    @property
    def w9_extension(self):
        return extension(self.w9_filename)

    @property
    def download_filename(self):
        return self.band.normalized_group_name + "_w9_form." + self.w9_extension

    @property
    def status(self):
        return self.w9_url if self.w9_url else ''


class BandStagePlot(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    filename = Column(UnicodeText)
    content_type = Column(UnicodeText)

    @property
    def url(self):
        return '../bands/view_stage_plot?id={}'.format(self.band.id) if self.uploaded_file else ''

    @property
    def fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'stage_plots', self.id)

    @property
    def uploaded_file(self):
        return os.path.exists(self.fpath)

    @property
    def stage_plot_extension(self):
        return extension(self.filename)

    @property
    def download_filename(self):
        return self.band.normalized_group_name + "_stage_plot." + self.stage_plot_extension

    @property
    def status(self):
        return self.url if self.url else ''


class BandPanel(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    wants_panel = Column(Choice(c.BAND_PANEL_OPTS), nullable=True)
    name = Column(UnicodeText)
    length = Column(UnicodeText)
    desc = Column(UnicodeText)
    tech_needs = Column(MultiChoice(c.TECH_NEED_OPTS))

    @property
    def status(self):
        return self.wants_panel_label


class BandMerch(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    selling_merch = Column(Choice(c.BAND_MERCH_OPTS), nullable=True)

    @property
    def status(self):
        return self.selling_merch_label


class BandCharity(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'), unique=True)
    donating = Column(Choice(c.BAND_CHARITY_OPTS), nullable=True)
    desc = Column(UnicodeText)

    @property
    def status(self):
        return self.donating_label
