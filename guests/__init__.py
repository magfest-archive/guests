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


@JinjaEnv.jinja_filter
def comma_join(xs, conjunction='and'):
    """
    Accepts a list of strings and separates them with commas as grammatically
    appropriate with a conjunction before the final entry. For example::

        >>> comma_join(['foo'])
        'foo'
        >>> comma_join(['foo', 'bar'])
        'foo and bar'
        >>> comma_join(['foo', 'bar', 'baz'])
        'foo, bar, and baz'
        >>> comma_join(['foo', 'bar', 'baz'], 'or')
        'foo, bar, or baz'
        >>> comma_join(['foo', 'bar', 'baz'], 'but never')
        'foo, bar, but never baz'

    """
    xs = list(xs)
    if len(xs) > 1:
        xs[-1] = conjunction + ' ' + xs[-1]
    return (', ' if len(xs) > 2 else ' ').join(xs)
