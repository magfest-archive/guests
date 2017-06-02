from bands import *


@all_renderable(c.BANDS)
class Root:
    def index(self, session, message=''):
        return {
            'message': message,
            'groups': session.query(Group).order_by('name').all()
        }

    def add_band(self, session, message='', **params):
        group = session.group(params, checkgroups=Group.all_checkgroups, bools=Group.all_bools,)
        if params.get('name') and params.get('first_name') and params.get('last_name') and params.get('email'):
            group.auto_recalc = False
            session.add(group)
            message = session.assign_badges(group, params['badges'], new_ribbon_type=c.BAND, paid=c.NEED_NOT_PAY)
            if not message:
                session.commit()
                leader = group.leader = group.attendees[0]
                leader.first_name, leader.last_name, leader.email = params.get('first_name'), params.get('last_name'), params.get('email')
                leader.placeholder = True
                message = check(leader)
                if not message:
                    group.band = Band()
                    session.commit()
                    raise HTTPRedirect("index?message={}{}", group.name, " has been uploaded")
                else:
                    session.delete(group)
            else:
                session.delete(group)
        return{
            'message': message,
            'group': group,
            'first_name': params.get('first_name') if 'first_name' in params else '',
            'last_name': params.get('last_name') if 'last_name' in params else '',
            'email': params.get('email') if 'email' in params else ''
        }

    @ajax
    def mark_as_band(self, session, group_id):
        group = session.group(group_id)
        if not group.leader:
            return {'message': '{} does not have an assigned group leader'.format(group.name)}

        if not group.band:
            group.band = Band()
            session.commit()

        return {
            'id': group.band.id,
            'message': '{} has been marked as a band'.format(group.name)
        }

    @ajax
    def remove_as_band(self, session, group_id):
        group = session.group(group_id)

        if group.band:
            group.band = None
            session.commit()

        return {
            'id': group.id,
            'message': '{} has been removed as a band'.format(group.name)
        }

    def band_info(self, session, message='', event_id=None, **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            if event_id:
                band.event_id = event_id
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
            'Payment', 'Vehicles', 'Load-In', 'Performance Time',
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
                band.payment, band.vehicles, band.estimated_loadin_minutes, band.estimated_performance_minutes,
                getattr(band.info, 'poc_phone', ''), getattr(band.info, 'performer_count', ''), getattr(band.info, 'bringing_vehicle', ''), getattr(band.info, 'vehicle_info', ''), getattr(band.info, 'arrival_time', ''),
                getattr(band.bio, 'desc', ''), getattr(band.bio, 'website', ''), getattr(band.bio, 'facebook', ''), getattr(band.bio, 'twitter', ''), getattr(band.bio, 'other_social_media', ''), absolute_pic_url,
                getattr(band.panel, 'wants_panel', ''), getattr(band.panel, 'name', ''), getattr(band.panel, 'length', ''), getattr(band.panel, 'desc', ''), ' / '.join(getattr(band.panel, 'panel_tech_needs_labels', '')),
                absolute_w9_url, absolute_stageplot_url,
                getattr(band.merch, 'selling_merch_label', ''),
                getattr(band.charity, 'donating_label', ''), getattr(band.charity, 'desc', '')
            ])
