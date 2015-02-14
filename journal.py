# -*- coding: utf-8 -*-

import os
import logging
import psycopg2
import markdown
import pygments
import jinja2
import datetime
from datetime import date

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config
from pyramid.events import NewRequest, subscriber
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import remember, forget
from cryptacular.bcrypt import BCRYPTPasswordManager
from waitress import serve
from contextlib import closing

here = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig()
log = logging.getLogger(__file__)

# Database queries
DB_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS entries (
        id serial PRIMARY KEY,
        title VARCHAR (127) NOT NULL,
        text TEXT NOT NULL,
        created TIMESTAMP NOT NULL
    ) '''
INSERT_ENTRY = '''
    INSERT INTO entries (title, text, created) VALUES (%s, %s, %s) '''
DB_ENTRIES_LIST = '''
    SELECT id, title, text, created FROM entries ORDER BY created DESC '''
INDIVIDUAL_ENTRY = '''
    SELECT id, title, text, created FROM entries WHERE id = %s '''


def connect_db(settings):
    return psycopg2.connect(settings['db'])

def init_db():
    settings = {}
    settings['db'] = os.environ.get(
        'DATABASE_URL', 'dbname=learning-journal user=Joel')
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    settings['auth.password'] = os.environ.get('AUTH_PASSWORD', 'secret')

    with closing(connect_db(settings)) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()

def close_connection(request):
    db = getattr(request, 'db', None)
    if db is not None:
        if request.exception is not None:
            db.rollback()
        else:
            db.commit()
        request.db.close()

def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('both username and password are required!')

    settings = request.registry.settings
    manager = BCRYPTPasswordManager()

    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')

    return manager.check(hashed, password)

@subscriber(NewRequest)
def open_connection(event):
    request = event.request
    settings = request.registry.settings
    request.db = connect_db(settings)
    request.add_finished_callback(close_connection)

def md(input):
    return markdown.markdown(input)

@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    '''Authenticate a user by username/password'''
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = "Login Failed"
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as e:
            error = str(e)

        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'error': error, 'username': username }

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)

@view_config(route_name='home', renderer='templates/list.jinja2')
def read_entries(request):
    cur = request.db.cursor()
    cur.execute(DB_ENTRIES_LIST)
    keys = ('id', 'title', 'text', 'created')
    entries = [dict(zip(keys, row)) for row in cur.fetchall()]
    for entry in entries:
        entry['text'] = (
            markdown.markdown(entry['text'], extensions=['codehilite',
                                                         'fenced_code'])
        )
    return {'entries': entries}

@view_config(route_name='add', request_method='POST')
def add(request):
    try:
        title = request.params.get('title', None)
        text = request.params.get('text', None)
        created = datetime.datetime.utcnow()
        request.db.cursor().execute(INSERT_ENTRY, [title, text, created])
    except psycopg2.Error:
        return HTTPInternalServerError
    return HTTPFound(request.route_url('home'))

@view_config(route_name='entry', renderer='templates/entry.jinja2')
def read(request):
    id = request.matchdict.get('id', None)
    cur = request.db.cursor()
    cur.execute(INDIVIDUAL_ENTRY, [id])
    keys = ('id', 'title', 'text', 'created')
    entry = dict(zip(keys, cur.fetchone()))
    return {'entry': entry }

@view_config(route_name='edit', renderer='templates/edit.jinja2')
def edit(request):
    """return a list of all entries as dicts"""
    id = request.matchdict.get('id', -1)
    cursor = request.db.cursor()
    cursor.execute(INDIVIDUAL_ENTRY, (id,))
    keys = ('id', 'title', 'text', 'created')
    entries = [dict(zip(keys, row)) for row in cursor.fetchall()]
    return {'entries': entries}

@view_config(route_name='update', request_method='POST')
def update(request):
    try:
        id = request.matchdict.get('id', -1)
        title = request.params.get('title', None)
        text = request.params.get('text', None)
        created = date.today()
        ENTRY_UPDATE = (
            "UPDATE entries SET title=%s, text=%s, created=%s WHERE id=%s;"
        )
        request.db.cursor().execute(ENTRY_UPDATE, [title, text, created, id])
    except psycopg2.Error:
        return HTTPInternalServerError
    return HTTPFound(request.route_url('home'))

def main():
    manager = BCRYPTPasswordManager()

    settings = {}
    settings['debug_all'] = os.environ.get('DEBUG', True)
    settings['reload_all'] = os.environ.get('DEBUG', True)
    settings['db'] = os.environ.get('DATABASE_URL',
                                    'dbname=learning-journal user=Joel')
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    settings['auth.password'] = os.environ.get('AUTH_PASSWORD',
                                               manager.encode('secret'))

    # secret value for session signing
    secret = os.environ.get('JOURNAL_SESSION_SECRET', 'itsaseekrit')
    session_factory = SignedCookieSessionFactory(secret)
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'anotherseekrit')

    jinja2.filters.FILTERS['markdown'] = md

    # configuration setup
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
        ),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.include('pyramid_jinja2')
    config.add_static_view('static', os.path.join(here, 'static'))

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('add', '/add')
    config.add_route('entry', '/post/{id}')
    config.add_route('edit', '/edit/{id}')
    config.add_route('update', '/update/{id}')
    config.scan()

    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
