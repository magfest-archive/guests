from bands import *


@all_renderable(c.BANDS)
class Root:

    def _required_message(self, params, fields):
        missing = [s for s in fields if not params.get(s, '').strip()]
        if missing:
            return '{} {} required'.format(
                comma_and([s.replace('_', ' ').title() for s in missing]),
                'is' if len(missing) == 1 else 'are')
        return ''

    def index(self, session, message='', filter='show-all'):
        return {
            'message': message,
            'groups': session.query(Group).order_by('name').all(),
            'groups_filter': filter
        }

    def add_band(self, session, message='', **params):
        group = session.group(params, checkgroups=Group.all_checkgroups, bools=Group.all_bools)
        if cherrypy.request.method == 'POST':
            message = self._required_message(
                params, ['name', 'first_name', 'last_name', 'email'])
            if not message:
                group.auto_recalc = False
                session.add(group)
                new_ribbon = c.BAND if params['group_type'] == c.BAND else None
                message = session.assign_badges(group, params.get('badges', 1), new_badge_type=c.GUEST_BADGE, new_ribbon_type=new_ribbon, paid=c.PAID_BY_GROUP)
            if not message:
                session.commit()
                leader = group.leader = group.attendees[0]
                leader.first_name, leader.last_name, leader.email = params.get('first_name'), params.get('last_name'), params.get('email')
                leader.placeholder = True
                message = check(leader)
                if not message:
                    group.band = Band()
                    group.band.group_type = params['group_type']
                    session.commit()
                    raise HTTPRedirect('index?message={} has been uploaded', group.name)
                else:
                    session.delete(group)

        return {
            'message': message,
            'group': group,
            'first_name': params.get('first_name', ''),
            'last_name': params.get('last_name', ''),
            'email': params.get('email', '')
        }

    @ajax
    def mark_as_band(self, session, group_id, group_type):
        group = session.group(group_id)
        if not group.leader:
            return {'message': '{} does not have an assigned group leader'.format(group.name)}

        if not group.band:
            group.band = Band()
            group.band.group_type = group_type
            session.commit()

        return {
            'id': group.band.id,
            'message': '{} has been marked as a {}'.format(group.name, group.band.group_type_label)
        }

    @ajax
    def remove_as_band(self, session, group_id):
        group = session.group(group_id)
        group_type_label = group.band.group_type_label

        if group.band:
            group.band = None
            session.commit()

        return {
            'id': group.id,
            'message': '{} has been removed as a {}'.format(group.name, group_type_label)
        }

    def group_info(self, session, message='', event_id=None, **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            if event_id:
                band.event_id = event_id
            if not message:
                raise HTTPRedirect('index?message={}{}', band.group.name, ' data uploaded')

        events = session.query(Event).filter_by(location=c.CONCERTS).order_by(Event.start_time).all()
        return {
            'band': band,
            'message': message,
            'events': [(event.id, event.name) for event in events]
        }

    @csv_file
    def everything(self, out, session):
        out.writerow([
            'Group Name', 'Primary Contact Email',
            'Payment', 'Vehicles', 'Hotel Rooms', 'Load-In', 'Performance Time',
            'PoC Cellphone', 'Performer Count', 'Bringing Vehicle', 'Vehicle Info', 'Arrival Time',
            'Bio', 'Website', 'Facebook', 'Twitter', 'Other Social Media', 'Bio Pic',
            'Wants Panel', 'Panel Name', 'Panel Description', 'Panel Length', 'Panel Tech Needs',
            'Completed W9', 'Stage Plot',
            'Selling Merchandise',
            'Charity Answer', 'Charity Donation'
        ])
        for band in session.query(Band).all():
            absolute_pic_url = convert_to_absolute_url(getattr(band.bio, 'pic_url', ''))
            absolute_w9_url = convert_to_absolute_url(getattr(band.taxes, 'w9_url', ''))
            absolute_stageplot_url = convert_to_absolute_url(getattr(band.stage_plot, 'url', ''))
            out.writerow([
                band.group.name, band.email,
                band.payment, band.vehicles, band.num_hotel_rooms, band.estimated_loadin_minutes, band.estimated_performance_minutes,
                getattr(band.info, 'poc_phone', ''), getattr(band.info, 'performer_count', ''), getattr(band.info, 'bringing_vehicle', ''), getattr(band.info, 'vehicle_info', ''), getattr(band.info, 'arrival_time', ''),
                getattr(band.bio, 'desc', ''), getattr(band.bio, 'website', ''), getattr(band.bio, 'facebook', ''), getattr(band.bio, 'twitter', ''), getattr(band.bio, 'other_social_media', ''), absolute_pic_url,
                getattr(band.panel, 'wants_panel', ''), getattr(band.panel, 'name', ''), getattr(band.panel, 'length', ''), getattr(band.panel, 'desc', ''), ' / '.join(getattr(band.panel, 'panel_tech_needs_labels', '')),
                absolute_w9_url, absolute_stageplot_url,
                getattr(band.merch, 'selling_merch_label', ''),
                getattr(band.charity, 'donating_label', ''), getattr(band.charity, 'desc', '')
            ])
