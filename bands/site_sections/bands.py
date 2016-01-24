from bands import *


@all_renderable()
class Root:
    def index(self, session, id, message=''):
        return {
            'message': message,
            'band': session.band(id)
        }

    def agreement(self, session, message='', **params):
        band = session.band(params, restricted=True)
        if cherrypy.request.method == 'POST':
            if not band.performer_count:
                message = 'You must tell us how many people are in your band'
            elif not band.poc_phone:
                message = 'You must enter an on-site point-of-contact cellphone number'
            elif not band.arrival_time:
                message = 'You must enter your expected arrival time'
            elif band.bringing_vehicle and not band.vehicle_info:
                message = 'You must provide your vehicle information'
            else:
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your band information has been uploaded')

        return {
            'band': band,
            'message': message
        }

    def bio(self, session, message='', bio_pic=None, **params):
        band = session.band(params, restricted=True)
        if cherrypy.request.method == 'POST':
            if not band.bio:
                message = 'Please provide a brief bio for our website'

            if not message and bio_pic:
                band.bio_pic_filename = bio_pic.filename
                band.bio_pic_content_type = bio_pic.content_type.value
                if band.bio_pic_extension not in c.ALLOWED_BIO_PIC_EXTENSIONS:
                    message = 'Bio pic must be one of ' + ', '.join(c.ALLOWED_BIO_PIC_EXTENSIONS)
                else:
                    with open(band.bio_pic_fpath, 'wb') as f:
                        shutil.copyfileobj(bio_pic.file, f)

            if not message:
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your bio information has been updated')

        return {
            'band': band,
            'message': message
        }

    def w9(self, session, id, message='', w9=None):
        band = session.band(id)
        if cherrypy.request.method == 'POST':
            band.w9_filename = w9.filename
            band.w9_content_type = w9.content_type.value
            if band.w9_extension not in c.ALLOWED_W9_EXTENSIONS:
                message = 'Uploaded file type must be one of ' + ', '.join(c.ALLOWED_W9_EXTENSIONS)
            else:
                with open(band.w9_fpath, 'wb') as f:
                    shutil.copyfileobj(w9.file, f)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'W9 uploaded')

        return {
            'band': band,
            'message': message
        }

    def stage_plot(self, session, id, message='', plot=None):
        band = session.band(id)
        if cherrypy.request.method == 'POST':
            band.stage_plot_filename = plot.filename
            band.stage_plot_content_type = plot.content_type.value
            if band.stage_plot_extension not in c.ALLOWED_STAGE_PLOT_EXTENSIONS:
                message = 'Uploaded file type must be one of ' + ', '.join(c.ALLOWED_STAGE_PLOT_EXTENSIONS)
            else:
                with open(band.stage_plot_fpath, 'wb') as f:
                    shutil.copyfileobj(plot.file, f)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Stage directions uploaded')

        return {
            'band': band,
            'message': message
        }

    def panel(self, session, message='', **params):
        band = session.band(params, checkgroups=['panel_tech_needs'])
        if cherrypy.request.method == 'POST':
            if not band.wants_panel:
                band.wants_panel = 0
                band.panel_name = band.panel_length = band.panel_desc = band.panel_tech_needs = ''
            elif not band.panel_name:
                message = 'Panel Name is a required field'
            elif not band.panel_length:
                message = 'Panel Length is a required field'
            elif not band.panel_desc:
                message = 'Panel Description is a required field'

            if not message:
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Panel preferences updated')

        return {
            'band': band,
            'message': message
        }

    def rock_island(self, session, message='', coverage=False, warning=False, **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            if not band.merch:
                message = 'You need to tell us whether and how you want to sell merchandise'
            elif band.merch == c.OWN_TABLE and not all([coverage, warning]):
                message = 'You cannot staff your own table without checking the boxes to agree to our conditions'
            else:
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your merchandise preferences have been saved')

        return {
            'band': band,
            'message': message
        }

    def charity(self, session, message='', **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            if not band.charity:
                message = 'You need to tell is whether you are donating anything'
            elif band.charity == c.DONATING and not band.charity_donation:
                message = 'You need to tell us what you intend to donate'
            else:
                if band.charity == c.NOT_DONATING:
                    band.charity_donation = ''
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your charity decisions have been saved')

        return {
            'band': band,
            'message': message
        }

    def view_bio_pic(self, session, id):
        band = session.band(id)
        return serve_file(band.bio_pic_fpath, name=band.bio_pic_filename, content_type=band.bio_pic_content_type)

    def view_w9(self, session, id):
        band = session.band(id)
        return serve_file(band.w9_fpath, name=band.w9_filename, content_type=band.w9_content_type)

    def view_stage_plot(self, session, id):
        band = session.band(id)
        return serve_file(band.stage_plot_fpath, name=band.stage_plot_filename, content_type=band.stage_plot_content_type)
