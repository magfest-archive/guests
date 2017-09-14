import re

import cherrypy
import pytest
from uber.utils import CSRFException

from bands import *
from bands.site_sections import band_admin


def _extract_message_from_html(html):
    match = re.search(r"var message = '(.*)';", html)
    return match.group(1) if match else None


@pytest.fixture()
def GET(monkeypatch):
    monkeypatch.setattr(cherrypy.request, 'method', 'GET')


@pytest.fixture()
def POST(monkeypatch):
    monkeypatch.setattr(cherrypy.request, 'method', 'POST')


@pytest.fixture()
def csrf_token(monkeypatch):
    token = '4a2cc6f4-bf9f-49d2-a925-00ff4e22ae4a'
    monkeypatch.setitem(cherrypy.session, 'csrf_token', token)
    monkeypatch.setitem(cherrypy.request.headers, 'CSRF-Token', token)
    yield token


@pytest.fixture()
def admin_attendee():
    with Session() as session:
        session.insert_test_admin_account()

    with Session() as session:
        attendee = session.query(Attendee).filter(
            Attendee.email == 'magfest@example.com').one()
        cherrypy.session['account_id'] = attendee.admin_account.id
        yield attendee
        cherrypy.session['account_id'] = None
        session.delete(attendee)


class TestAddBand(object):

    def _add_band_response(self, **params):
        response = band_admin.Root().add_band(**params)
        if isinstance(response, bytes):
            response = response.decode('utf-8')
        response = response.strip()
        assert response.startswith('<!DOCTYPE HTML>')
        return response

    def test_GET(self, GET, admin_attendee):
        response = self._add_band_response()
        message = _extract_message_from_html(response)
        assert message == ''

    def test_POST_requires_csrf_token(self, POST, admin_attendee):
        with pytest.raises(HTTPRedirect, match='CSRF'):
            band_admin.Root().add_band()

    @pytest.mark.parametrize('params,message_start', [
        (dict(), 'Name, First Name, Last Name, and Email are'),
        (dict(name='Group1', first_name='Al'), 'Last Name and Email are'),
        (dict(name='Group1', first_name='Al', last_name='Bert'), 'Email is')])
    def test_POST_required_fields(
            self, POST, csrf_token, admin_attendee, params, message_start):
        response = self._add_band_response(**params)
        message = _extract_message_from_html(response)
        assert message.startswith(message_start)

        with Session() as session:
            assert session.query(Group).filter(
                Group.name == 'Group1').first() is None

    def test_POST_creates_group(self, POST, csrf_token, admin_attendee):
        with pytest.raises(HTTPRedirect, match='Group1 has been uploaded'):
            response = self._add_band_response(
                name='Group1',
                admin_notes='Stuff',
                first_name='Al',
                last_name='Bert',
                email='al@example.com',
                group_type=c.BAND,
                badges=4)

        with Session() as session:
            group = session.query(Group).filter(Group.name == 'Group1').first()
            assert group
            assert group.auto_recalc == False
            assert group.admin_notes == 'Stuff'
            assert group.leader
            assert group.leader.first_name == 'Al'
            assert group.leader.last_name == 'Bert'
            assert group.leader.email == 'al@example.com'
            assert group.leader.placeholder == True
            assert group.leader.paid == c.PAID_BY_GROUP
            assert group.band
            assert group.badges == 4
            for attendee in group.attendees:
                assert attendee.paid == c.PAID_BY_GROUP
                assert attendee.badge_type == c.GUEST_BADGE
                assert c.BAND in attendee.ribbon_ints
