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
        if not group.band:
            group.band = Band()
            session.commit()
        return {'message': '{} has been marked as a band'.format(group.name)}

    @unrestricted
    def confirm(self, session, message='', **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            message = check(band)
            if not message:
                raise HTTPRedirect('confirm?id={}&message={}', band.id, 'Whatever we end up putting on this form has been successfully uploaded')

        return {
            'band': band,
            'message': message
        }
