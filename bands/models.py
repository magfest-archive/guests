from bands import *


def extension(filename):
    return filename.split('.')[-1].lower()


@Session.model_mixin
class Group:
    band = relationship('Band', backref='group', uselist=False)


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

    @property
    def all_badges_claimed(self):
        return not any(a.is_unassigned for a in self.group.attendees)


class BandInfo(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    poc_phone = Column(UnicodeText)
    performer_count = Column(Integer, default=0)
    bringing_vehicle = Column(Boolean, default=False)
    vehicle_info = Column(UnicodeText)
    arrival_time = Column(UnicodeText)
    vehicles = Column(Integer, default=1, admin_only=True)
    estimated_loadin_minutes = Column(Integer, default=60, admin_only=True)
    estimated_performance_minutes = Column(Integer, default=60, admin_only=True)

    @property
    def email(self):
        return self.group.email

    @property
    def estimated_performer_count(self):
        return len([a for a in self.band.group.attendees if a.badge_type == c.GUEST_BADGE]) or 0

    @property
    def performance_minutes(self):
        return self.event.minutes if self.event_id else self.estimated_performance_minutes

    @property
    def completed(self):
        return self.poc_phone


class BandBio(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    bio = Column(UnicodeText)
    website = Column(UnicodeText)
    facebook = Column(UnicodeText)
    twitter = Column(UnicodeText)
    other_social_media = Column(UnicodeText)

    bio_pic_filename = Column(UnicodeText)
    bio_pic_content_type = Column(UnicodeText)

    @property
    def bio_pic_url(self):
        return '{}/bands/view_bio_pic?id={}'.format(c.URL_BASE, self.id) if self.uploaded_bio_pic else ''

    @property
    def bio_pic_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'bio_pics', self.id)

    @property
    def uploaded_bio_pic(self):
        return os.path.exists(self.bio_pic_fpath)

    @property
    def bio_pic_extension(self):
        return extension(self.bio_pic_filename)

    @property
    def completed(self):
        return self.bio


class BandTaxes(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    w9_filename = Column(UnicodeText)
    w9_content_type = Column(UnicodeText)

    @property
    def w9_url(self):
        return '{}/bands/view_w9?id={}'.format(c.URL_BASE, self.id) if self.completed_w9 else ''

    @property
    def w9_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'w9_forms', self.id)

    @property
    def w9_extension(self):
        return extension(self.w9_filename)

    @property
    def completed(self):
        return self.w9_filename


class BandStagePlot(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    stage_plot_filename = Column(UnicodeText)
    stage_plot_content_type = Column(UnicodeText)

    @property
    def stage_plot_url(self):
        return '{}/bands/view_stage_plot?id={}'.format(c.URL_BASE, self.id) if self.uploaded_stage_plot else ''

    @property
    def stage_plot_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'stage_plots', self.id)

    @property
    def uploaded_stage_plot(self):
        return os.path.exists(self.stage_plot_fpath)

    @property
    def stage_plot_extension(self):
        return extension(self.stage_plot_filename)

    @property
    def completed(self):
        return self.uploaded_stage_plot


class BandPanel(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    # This needs to be a nullable integer rather than a nullable boolean to prevent SQLAlchemy from setting a False value
    # when it's instantiated and saved without this field being set.  An annoying but necessary workaround.
    wants_panel = Column(Integer, nullable=True, default=None)
    panel_name = Column(UnicodeText)
    panel_length = Column(UnicodeText)
    panel_desc = Column(UnicodeText)
    panel_tech_needs = Column(MultiChoice(c.TECH_NEED_OPTS))

    @property
    def completed(self):
        return self.wants_panel is not None


class BandMerch(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    merch = Column(Choice(c.BAND_MERCH_OPTS), nullable=True)

    @property
    def completed(self):
        return self.merch is not None


class BandCharity(MagModel):
    band_id = Column(UUID, ForeignKey('band.id'))
    charity = Column(Choice(c.BAND_CHARITY_OPTS), nullable=True)
    charity_donation = Column(UnicodeText)

    @property
    def completed(self):
        return self.charity is not None
