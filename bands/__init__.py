import shutil

from cherrypy.lib.static import serve_file

from uber.common import *
from panels import *
from bands._version import __version__
from bands.config import *
from bands.models import *
import bands.model_checks
import bands.automated_emails

static_overrides(join(bands_config['module_root'], 'static'))
template_overrides(join(bands_config['module_root'], 'templates'))
mount_site_sections(bands_config['module_root'])

c.MENU['People'].append_menu_item(
    MenuItem(access=c.BANDS, name='Bands', href='../band_admin/?filter=only-bands')
)
c.MENU['People'].append_menu_item(
    MenuItem(access=c.BANDS, name='Guests', href='../band_admin/?filter=only-guests')
)
