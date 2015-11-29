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

        return {
            'id': group.band.id,
            'message': '{} has been marked as a band'.format(group.name)
        }

    def band_info(self, session, message='', **params):
        band = session.band(params)
        if cherrypy.request.method == 'POST':
            raise HTTPRedirect('index?message={}{}', band.group.name, ' data uploaded')

        return {
            'band': band,
            'message': message
        }
