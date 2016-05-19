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
            out.writerow([
                band.group.name, band.email,
                band.payment, band.vehicles, band.estimated_loadin_minutes, band.estimated_performance_minutes,
                getattr(band.info, 'poc_phone', ''), getattr(band.info, 'performer_count', ''), getattr(band.info, 'bringing_vehicle', ''), getattr(band.info, 'vehicle_info', ''), getattr(band.info, 'arrival_time', ''),
                getattr(band.bio, 'desc', ''), getattr(band.bio, 'website', ''), getattr(band.bio, 'facebook', ''), getattr(band.bio, 'twitter', ''), getattr(band.bio, 'other_social_media', ''), getattr(band.bio, 'pic_url', ''),
                getattr(band.panel, 'wants_panel', ''), getattr(band.panel, 'name', ''), getattr(band.panel, 'length', ''), getattr(band.panel, 'desc', ''), ' / '.join(getattr(band.panel, 'panel_tech_needs_labels', '')),
                getattr(band.taxes, 'w9_url', ''), getattr(band.stage_plot, 'url', ''),
                getattr(band.merch, 'selling_merch_label', ''),
                getattr(band.charity, 'donating_label', ''), getattr(band.charity, 'desc', '')
            ])
