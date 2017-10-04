import shutil

from cherrypy.lib.static import serve_file

from uber.common import *
from panels import *
from guests._version import __version__
from guests.config import *
from guests.models import *
import guests.model_checks
import guests.automated_emails

static_overrides(join(guests_config['module_root'], 'static'))
template_overrides(join(guests_config['module_root'], 'templates'))
mount_site_sections(guests_config['module_root'])

c.MENU['People'].append_menu_item(
    MenuItem(access=c.BANDS, name='Bands', href='../guest_admin/?filter=only-bands')
)
c.MENU['People'].append_menu_item(
    MenuItem(access=c.BANDS, name='Guests', href='../guest_admin/?filter=only-guests')
)
