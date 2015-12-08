from bands import *


@Session.model_mixin
class Group:
    band = relationship('Band', backref='group', uselist=False)


@Session.model_mixin
class Event:
    band = relationship('Band', backref='event')


class Band(MagModel):
    group_id = Column(UUID, ForeignKey('group.id'))
    event_id = Column(UUID, ForeignKey('event.id'), nullable=True)

    payment = Column(Integer, default=0, admin_only=True)
    vehicles = Column(Integer, default=1, admin_only=True)
    estimated_loadin_minutes = Column(Integer, default=60, admin_only=True)
    estimated_performance_minutes = Column(Integer, default=60, admin_only=True)

    poc_phone = Column(UnicodeText)
    performer_count = Column(Integer, default=0)
    bringing_vehicle = Column(Boolean, default=False)
    vehicle_info = Column(UnicodeText)
    arrival_time = Column(UnicodeText)

    bio = Column(UnicodeText)
    website = Column(UnicodeText)
    facebook = Column(UnicodeText)
    twitter = Column(UnicodeText)
    other_social_media = Column(UnicodeText)

    w9_filename = Column(UnicodeText)
    w9_extension = Column(UnicodeText)
    w9_content_type = Column(UnicodeText)

    bio_pic_filename = Column(UnicodeText)
    bio_pic_extension = Column(UnicodeText)
    bio_pic_content_type = Column(UnicodeText)

    stage_plot_filename = Column(UnicodeText)
    stage_plot_extension = Column(UnicodeText)
    stage_plot_content_type = Column(UnicodeText)

    wants_panel = Column(Boolean, nullable=True, default=None)
    panel_name = Column(UnicodeText)
    panel_length = Column(UnicodeText)
    panel_desc = Column(UnicodeText)
    panel_tech_needs = Column(MultiChoice(c.TECH_NEED_OPTS))

    @property
    def email(self):
        return self.group.email

    @property
    def estimated_performer_count(self):
        return len([a for a in self.group.attendees if a.badge_type == c.GUEST_BADGE])

    @property
    def w9_url(self):
        return '../bands/view_w9?id={}'.format(self.id)

    @property
    def bio_pic_url(self):
        return '../bands/view_bio_pic?id={}'.format(self.id)

    @property
    def w9_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'w9_forms', self.id)

    @property
    def bio_pic_fpath(self):
        return os.path.join(bands_config['root'], 'uploaded_files', 'bio_pics', self.id)

    @property
    def uploaded_bio_pic(self):
        return os.path.exists(self.bio_pic_fpath)

    @property
    def all_badges_claimed(self):
        return not any(a.is_unassigned for a in self.group.attendees)

    @property
    def completed_agreement(self):
        return bool(self.poc_phone)

    @property
    def completed_bio(self):
        return bool(self.bio)

    @property
    def completed_w9(self):
        return os.path.exists(self.w9_fpath)

    @property
    def completed_panel(self):
        return self.wants_panel is not None

    @property
    def completed_stage_agreement(self):
        return False  # this will be implemented after getting some feedback from the music department about what is involved
