from bands import *


@all_renderable(c.BANDS)
class Root:
    def index(self, session, message=''):
        return {
            'message': message,
            'groups': session.query(Group).order_by('name').all()
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

    def band_info(self, session, message='', event_id=None, **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            if event_id:
                band.event_id = event_id
            raise HTTPRedirect('index?message={}{}', band.group.name, ' data uploaded')

        return {
            'band': band,
            'message': message,
            'events': [
                (event.id, event.name)
                for event in session.query(Event).filter_by(location=c.CONCERTS).order_by(Event.start_time).all()
            ]
        }

    @csv_file
    def everything(self, out, session):
        out.writerow([
            'Group Name', 'Primary Contact Email',
            'Payment', 'Vehicles', 'Load-In', 'Performance Time',
            'PoC Cellphone', 'Performer Count', 'Bringing Vehicle', 'Vehicle Info', 'Arrival Time',
            'Bio', 'Website', 'Facebook', 'Twitter', 'Other Social Media',
            'Wants Panel', 'Panel Name', 'Panel Description', 'Panel Length', 'Panel Tech Needs'
        ])
        for band in session.query(Band).all():
            out.writerow([
                band.group.name, band.email,
                band.payment, band.vehicles, band.estimated_loadin_minutes, band.estimated_performance_minutes,
                band.poc_phone, band.performer_count, band.bringing_vehicle, band.vehicle_info, band.arrival_time,
                band.bio, band.website, band.facebook, band.twitter, band.other_social_media,
                band.wants_panel, band.panel_name, band.panel_length, band.panel_desc, ' / '.join(band.panel_tech_needs_labels)
            ])
