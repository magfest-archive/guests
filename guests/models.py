from guests import *
from sideboard.config import uniquify


def extension(filename):
    return filename.split('.')[-1].lower()


@Session.model_mixin
class Group:
    guest = relationship('GuestGroup', backref='group', uselist=False)


@Session.model_mixin
class Attendee:
    @property
    def guest_group(self):
        """
        :return: The Guest Group this attendee is part of (either as a guest or a +1 comp), or None if not
        """
        return self.group and self.group.guest


@Session.model_mixin
class Event:
    guest = relationship('GuestGroup', backref='event')


class GuestGroup(MagModel):
    group_id = Column(UUID, ForeignKey('group.id'))
    event_id = Column(UUID, ForeignKey('event.id'), nullable=True)
    group_type = Column(Choice(c.GROUP_TYPE_OPTS), default=c.BAND)
    info = relationship('GuestInfo', backref=backref('guest', load_on_pending=True), uselist=False)
    bio = relationship('GuestBio', backref=backref('guest', load_on_pending=True), uselist=False)
    taxes = relationship('GuestTaxes', backref=backref('guest', load_on_pending=True), uselist=False)
    stage_plot = relationship('GuestStagePlot', backref=backref('guest', load_on_pending=True), uselist=False)
    panel = relationship('GuestPanel', backref=backref('guest', load_on_pending=True), uselist=False)
    merch = relationship('GuestMerch', backref=backref('guest', load_on_pending=True), uselist=False)
    charity = relationship('GuestCharity', backref=backref('guest', load_on_pending=True), uselist=False)
    autograph = relationship('GuestAutograph', backref=backref('guest', load_on_pending=True), uselist=False)
    interview = relationship('GuestInterview', backref=backref('guest', load_on_pending=True), uselist=False)
    travel_plans = relationship('GuestTravelPlans', backref=backref('guest', load_on_pending=True), uselist=False)

    num_hotel_rooms = Column(Integer, default=1, admin_only=True)
    payment = Column(Integer, default=0, admin_only=True)
    vehicles = Column(Integer, default=1, admin_only=True)
    estimated_loadin_minutes = Column(Integer, default=c.DEFAULT_LOADIN_MINUTES, admin_only=True)
    estimated_performance_minutes = Column(Integer, default=c.DEFAULT_PERFORMANCE_MINUTES, admin_only=True)
    email_model_name = 'guest'

    def __getattr__(self, name):
        """
        If someone tries to access a property called, e.g., info_status, and the named property doesn't exist, we
        instead call self.status. This allows us to refer to status config options indirectly, which in turn
        allows us to override certain status options on a case-by-case basis. This is helpful for a couple of
        properties here, but it's vital to allow events to control group checklists with granularity.
        """
        if name.endswith('_status'):
            return self.status(name.rsplit('_', 1)[0])
        else:
            return super(GuestGroup, self).__getattr__(name)

    def deadline_from_model(self, model):
        return getattr(c, str(self.group_type_label).upper() + "_" + str(model).upper() + "_DEADLINE", None)

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

    @property
    def badges_status(self):
        return str(self.group.unregistered_badges) + " Unclaimed" if self.group.unregistered_badges else "Yes"

    @property
    def taxes_status(self):
        return "Not Needed" if not self.payment else self.status('taxes')

    @property
    def panel_status(self):
        return str(len(self.group.leader.panel_applications)) + " Panel Application(s)" \
            if self.group.leader.panel_applications else self.status('panel')

    def status(self, model):
        """
        This is a safe way to check if a step has been completed and what its status is for a particular group.
        It checks for a custom 'status' property for the step; if that doesn't exist, it will attempt to return
        True if an ID of the step exists or an empty string if not. If there's no corresponding deadline for the
        model we're checking, we return "N/A"

        :param model: This should match one of the relationship columns in the GuestGroup class, e.g., 'bio' or 'taxes'
        :return: Returns either the 'status' property of the model, "N/A," True, or an empty string.
        """

        if not self.deadline_from_model(model):
            return "N/A"

        subclass = getattr(self, model, None)
        return getattr(subclass, 'status', getattr(subclass, 'id')) if subclass else ''


class GuestInfo(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    poc_phone = Column(UnicodeText)
    performer_count = Column(Integer, default=0)
    bringing_vehicle = Column(Boolean, default=False)
    vehicle_info = Column(UnicodeText)
    arrival_time = Column(UnicodeText)

    @property
    def status(self):
        return "Yes" if self.poc_phone else ""


class GuestBio(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    desc = Column(UnicodeText)
    website = Column(UnicodeText)
    facebook = Column(UnicodeText)
    twitter = Column(UnicodeText)
    other_social_media = Column(UnicodeText)
    teaser_song_url = Column(UnicodeText)

    pic_filename = Column(UnicodeText)
    pic_content_type = Column(UnicodeText)

    @property
    def pic_url(self):
        return '../guests/view_bio_pic?id={}'.format(self.guest.id) if self.uploaded_pic else ''

    @property
    def pic_fpath(self):
        return os.path.join(guests_config['root'], 'uploaded_files', 'bio_pics', self.id)

    @property
    def uploaded_pic(self):
        return os.path.exists(self.pic_fpath)

    @property
    def pic_extension(self):
        return extension(self.pic_filename)

    @property
    def download_filename(self):
        return self.guest.normalized_group_name + "_bio_pic." + self.pic_extension

    @property
    def status(self):
        return "Yes" if self.desc else ""


class GuestTaxes(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    w9_filename = Column(UnicodeText)
    w9_content_type = Column(UnicodeText)

    @property
    def w9_url(self):
        return '../guests/view_w9?id={}'.format(self.guest.id) if self.w9_filename else ''

    @property
    def w9_fpath(self):
        return os.path.join(guests_config['root'], 'uploaded_files', 'w9_forms', self.id)

    @property
    def w9_extension(self):
        return extension(self.w9_filename)

    @property
    def download_filename(self):
        return self.guest.normalized_group_name + "_w9_form." + self.w9_extension

    @property
    def status(self):
        return self.w9_url if self.w9_url else ''


class GuestStagePlot(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    filename = Column(UnicodeText)
    content_type = Column(UnicodeText)

    @property
    def url(self):
        return '../guests/view_stage_plot?id={}'.format(self.guest.id) if self.uploaded_file else ''

    @property
    def fpath(self):
        return os.path.join(guests_config['root'], 'uploaded_files', 'stage_plots', self.id)

    @property
    def uploaded_file(self):
        return os.path.exists(self.fpath)

    @property
    def stage_plot_extension(self):
        return extension(self.filename)

    @property
    def download_filename(self):
        return self.guest.normalized_group_name + "_stage_plot." + self.stage_plot_extension

    @property
    def status(self):
        return self.url if self.url else ''


class GuestPanel(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    wants_panel = Column(Choice(c.GUEST_PANEL_OPTS), nullable=True)
    name = Column(UnicodeText)
    length = Column(UnicodeText)
    desc = Column(UnicodeText)
    tech_needs = Column(MultiChoice(c.TECH_NEED_OPTS))
    other_tech_needs = Column(UnicodeText)

    @property
    def status(self):
        return self.wants_panel_label


class GuestMerch(MagModel):
    _inventory_param_regex = re.compile(r'^inventory_([\w_\-]+?)_(\d+)$')
    _inventory_image_regex = re.compile(r'^image(|\-\d+)$')
    _inventory_audio_regex = re.compile(r'^audio(|\-\d+)$')

    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    selling_merch = Column(Choice(c.GUEST_MERCH_OPTS), nullable=True)
    inventory = Column(JSON, default=[], server_default='[]')
    bringing_boxes = Column(UnicodeText)
    extra_info = Column(UnicodeText)
    tax_phone = Column(UnicodeText)

    @property
    def rock_island_url(self):
        return '../guest_admin/rock_island?id={}'.format(self.guest_id)

    @property
    def rock_island_csv_url(self):
        return '../guest_admin/rock_island_csv?id={}'.format(self.guest_id)

    @property
    def status(self):
        return self.selling_merch_label

    @presave_adjustment
    def tax_phone_from_poc_phone(self):
        if self.selling_merch == c.OWN_TABLE and not self.tax_phone:
            self.tax_phone = self.guest.info.poc_phone

    def _extract_inventory_params(self, params):
        inventory = defaultdict(dict)
        for param_name, value in params.items():
            match = self._inventory_param_regex.match(param_name)
            if match:
                name = match.group(1)
                item_number = int(match.group(2))
                if not name.startswith('quantity') or value:
                    inventory[item_number][name] = value
        for item_number, item in inventory.items():
            if not item.get('id'):
                item['id'] = str(uuid.uuid4())
        return [item for (item_number, item) in sorted(inventory.items())]

    def _save_inventory_item_file(self, item, name, extensions=set()):
        messages = []
        download_filename_attr = '{}_download_filename'.format(name)
        filename_attr = '{}_filename'.format(name)
        content_type_attr = '{}_content_type'.format(name)
        file = None
        if name in item:
            file = item[name]
            del item[name]
            if getattr(file, 'filename', None):
                if extensions and extension(file.filename) not in extensions:
                    item[download_filename_attr] = None
                    item[filename_attr] = None
                    item[content_type_attr] = None
                    messages.append('Files must be one of ' + ', '.join(extensions))
                else:
                    item[download_filename_attr] = file.filename
                    item[filename_attr] = str(uuid.uuid4())
                    item[content_type_attr] = file.content_type.value
                    with open(self.inventory_path(item[filename_attr]), 'wb') as f:
                        shutil.copyfileobj(file.file, f)

        for attr in (download_filename_attr, filename_attr, content_type_attr):
            if not item.get(attr):
                del item[attr]

        return '\n'.join(uniquify(messages))

    @classmethod
    def total_quantity(cls, item):
        total_quantity = 0
        for attr in filter(lambda s: s.startswith('quantity'), item.keys()):
            total_quantity += int(item[attr] if item[attr] else 0)
        return total_quantity

    @classmethod
    def item_subcategories(cls, item_type):
        s = { getattr(c, s): s for s in c.MERCH_TYPES_VARS }[int(item_type)]
        return (
            getattr(c, '{}_VARIETIES'.format(s), defaultdict(lambda: {})),
            getattr(c, '{}_CUTS'.format(s), defaultdict(lambda: {})),
            getattr(c, '{}_SIZES'.format(s), defaultdict(lambda: {})))

    @classmethod
    def item_subcategories_opts(cls, item_type):
        s = { getattr(c, s): s for s in c.MERCH_TYPES_VARS }[int(item_type)]
        return (
            getattr(c, '{}_VARIETIES_OPTS'.format(s), defaultdict(lambda: [])),
            getattr(c, '{}_CUTS_OPTS'.format(s), defaultdict(lambda: [])),
            getattr(c, '{}_SIZES_OPTS'.format(s), defaultdict(lambda: [])))

    @classmethod
    def line_items(cls, item):
        line_items = []
        for attr in filter(lambda s: s.startswith('quantity-'), item.keys()):
            if int(item[attr] if item[attr] else 0) > 0:
                line_items.append(attr)

        varieties, cuts, sizes = [[v for (v, _) in x] for x in cls.item_subcategories_opts(item['type'])]
        def _line_item_sort_key(line_item):
            variety, cut, size = cls.line_item_to_types(line_item)
            return (
                varieties.index(variety) if variety else 0,
                cuts.index(cut) if cut else 0,
                sizes.index(size) if size else 0)

        return sorted(line_items, key=_line_item_sort_key)

    @classmethod
    def line_item_to_types(cls, line_item):
        return [int(s) for s in line_item.split('-')[1:]]

    @classmethod
    def line_item_to_string(cls, item, line_item):
        variety_value, cut_value, size_value = cls.line_item_to_types(line_item)

        varieties, cuts, sizes = cls.item_subcategories(item['type'])
        variety_label = varieties.get(variety_value, '').strip()
        if not size_value and not cut_value:
            return variety_label + ' - One size only'

        size_label = sizes.get(size_value, '').strip()
        cut_label = cuts.get(cut_value, '').strip()

        parts = [variety_label]
        if cut_label:
            parts.append(cut_label)
        if size_label:
            parts.extend(['-', size_label])
        return ' '.join(parts)

    @classmethod
    def inventory_path(cls, file):
        return os.path.join(guests_config['root'], 'uploaded_files', 'inventory', file)

    def inventory_url(self, inventory_id, name):
        return '../guests/view_inventory_file?id={}&inventory_id={}&name={}'.format(self.id, inventory_id, name)

    def inventory_item(self, id):
        for item in self.inventory:
            if item.get('id') == id:
                return item
        return None

    def merge_inventory(self, params):
        inventory = self._extract_inventory_params(params)
        for item in inventory:
            for name in [s for s in item.keys() if self._inventory_image_regex.match(s)]:
                self._save_inventory_item_file(item, name, c.ALLOWED_INVENTORY_IMAGE_EXTENSIONS)
            for name in [s for s in item.keys() if self._inventory_audio_regex.match(s)]:
                self._save_inventory_item_file(item, name, c.ALLOWED_INVENTORY_AUDIO_EXTENSIONS)
        self.inventory = inventory


class GuestCharity(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    donating = Column(Choice(c.GUEST_CHARITY_OPTS), nullable=True)
    desc = Column(UnicodeText)

    @property
    def status(self):
        return self.donating_label

    @presave_adjustment
    def no_desc_if_not_donating(self):
        if self.donating == c.NOT_DONATING:
            self.desc = ''


class GuestAutograph(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    num = Column(Integer, default=0)
    length = Column(Integer, default=60)  # session length in minutes

    @presave_adjustment
    def no_length_if_zero_autographs(self):
        if not self.num:
            self.length = 0


class GuestInterview(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    will_interview = Column(Boolean, default=False)
    email = Column(UnicodeText)
    direct_contact = Column(Boolean, default=False)

    @presave_adjustment
    def no_details_if_no_interview(self):
        if not self.will_interview:
            self.email = ''
            self.direct_contact = False


class GuestTravelPlans(MagModel):
    guest_id = Column(UUID, ForeignKey('guest_group.id'), unique=True)
    modes = Column(MultiChoice(c.GUEST_TRAVEL_OPTS))
    modes_text = Column(UnicodeText)
    details = Column(UnicodeText)
