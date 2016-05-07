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
            'Bio', 'Website', 'Facebook', 'Twitter', 'Other Social Media', 'Bio Pic',
            'Wants Panel', 'Panel Name', 'Panel Description', 'Panel Length', 'Panel Tech Needs',
            'Completed W9', 'Stage Plot',
            'Selling Merchandise',
            'Charity Answer', 'Charity Donation'
        ])
        for band in session.query(Band).all():
            out.writerow([
                band.group.name, band.info.email,
                band.payment, band.info.vehicles, band.info.estimated_loadin_minutes, band.info.estimated_performance_minutes,
                band.info.poc_phone, band.info.performer_count, band.info.bringing_vehicle, band.info.vehicle_info, band.info.arrival_time,
                band.bio.desc, band.bio.website, band.bio.facebook, band.bio.twitter, band.bio.other_social_media, band.bio.pic_url,
                band.panel.wants_panel, band.panel.name, band.panel.length, band.panel.desc, ' / '.join(band.panel.panel_tech_needs_labels),
                band.taxes.w9_url, band.stage_plot.url,
                band.merch.merch_label if band.merch else '',
                band.charity.charity_label if band.charity else '', band.charity.desc
            ])
