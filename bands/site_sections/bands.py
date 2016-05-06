from bands import *


@all_renderable()
class Root:
    def index(self, session, id, message=''):
        return {
            'message': message,
            'band': session.band(id)
        }

    def agreement(self, session, band_id, message='', **params):
        band_info = session.band_info(params, restricted=True)
        if cherrypy.request.method == 'POST':
            if not band_info.performer_count:
                message = 'You must tell us how many people are in your band'
            elif not band_info.poc_phone:
                message = 'You must enter an on-site point-of-contact cellphone number'
            elif not band_info.arrival_time:
                message = 'You must enter your expected arrival time'
            elif band_info.bringing_vehicle and not band.info.vehicle_info:
                message = 'You must provide your vehicle information'
            else:
                raise HTTPRedirect('index?id={}&message={}', band_info.band_id, 'Your band information has been uploaded')

        return {
            'band': band_info,
            'message': message
        }

    def bio(self, session, band_id, message='', bio_pic=None, **params):
        band_bio = session.band_bio(params, restricted=True)
        band_bio.band_id = band_id
        if cherrypy.request.method == 'POST':
            if not band_bio.bio:
                message = 'Please provide a brief bio for our website'

            if not message:
                raise HTTPRedirect('index?id={}&message={}', band_bio.band_id, 'Your bio information has been updated')

        return {
            'band': band_bio,
            'message': message
        }

    def w9(self, session, id, message='', w9=None):
        band = session.band(id)
        if cherrypy.request.method == 'POST':
            band.taxes.w9_filename = w9.filename
            band.taxes.w9_content_type = w9.content_type.value
            if band.taxes.w9_extension not in c.ALLOWED_W9_EXTENSIONS:
                message = 'Uploaded file type must be one of ' + ', '.join(c.ALLOWED_W9_EXTENSIONS)
            else:
                with open(band.taxes.w9_fpath, 'wb') as f:
                    shutil.copyfileobj(w9.file, f)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'W9 uploaded')

        return {
            'band': band,
            'message': message
        }

    def stage_plot(self, session, id, message='', plot=None):
        band = session.band(id)
        if cherrypy.request.method == 'POST':
            band.stage_plot.stage_plot_filename = plot.filename
            band.stage_plot.stage_plot_content_type = plot.content_type.value
            if band.stage_plot.stage_plot_extension not in c.ALLOWED_STAGE_PLOT_EXTENSIONS:
                message = 'Uploaded file type must be one of ' + ', '.join(c.ALLOWED_STAGE_PLOT_EXTENSIONS)
            else:
                with open(band.stage_plot.stage_plot_fpath, 'wb') as f:
                    shutil.copyfileobj(plot.file, f)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Stage directions uploaded')

        return {
            'band': band,
            'message': message
        }

    def panel(self, session, message='', **params):
        band = session.band(params, checkgroups=['panel_tech_needs'])
        if cherrypy.request.method == 'POST':
            if not band.panel.wants_panel:
                band.panel.wants_panel = 0
                band.panel.panel_name = band.panel.panel_length = band.panel.panel_desc = band.panel.panel_tech_needs = ''
            elif not band.panel.panel_name:
                message = 'Panel Name is a required field'
            elif not band.panel.panel_length:
                message = 'Panel Length is a required field'
            elif not band.panel.panel_desc:
                message = 'Panel Description is a required field'

            if not message:
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Panel preferences updated')

        return {
            'band': band,
            'message': message
        }

    def rock_island(self, session, message='', coverage=False, warning=False, **params):
        band.merch = session.band.merch(params)
        if cherrypy.request.method == 'POST':
            if not band.merch.merch:
                message = 'You need to tell us whether and how you want to sell merchandise'
            elif band.merch.merch == c.OWN_TABLE and not all([coverage, warning]):
                message = 'You cannot staff your own table without checking the boxes to agree to our conditions'
            else:
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your merchandise preferences have been saved')

        return {
            'band': band,
            'message': message
        }

    def charity(self, session, message='', **params):
        band.charity = session.charity.band(params)
        if cherrypy.request.method == 'POST':
            if not band.charity.charity:
                message = 'You need to tell is whether you are donating anything'
            elif band.charity.charity == c.DONATING and not band.charity.charity_donation:
                message = 'You need to tell us what you intend to donate'
            else:
                if band.charity.charity == c.NOT_DONATING:
                    band.charity.charity_donation = ''
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your charity decisions have been saved')

        return {
            'band': band,
            'message': message
        }

    def view_bio_pic(self, session, id):
        band = session.band(id)
        return serve_file(band.bio.bio_pic_fpath, name=band.bio.bio_pic_filename, content_type=band.bio.bio_pic_content_type)

    def view_w9(self, session, id):
        band = session.band(id)
        return serve_file(band.taxes.w9_fpath, name=band.taxes.w9_filename, content_type=band.taxes.w9_content_type)

    def view_stage_plot(self, session, id):
        band = session.band(id)
        return serve_file(band.stage_plot.stage_plot_fpath, name=band.stage_plot.stage_plot_filename, content_type=band.stage_plot.stage_plot_content_type)
