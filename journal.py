# -*- coding: utf-8 -*-
import os
import logging
import psycopg2
import datetime
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config
from pyramid.events import NewRequest, subscriber
from waitress import serve
from contextlib import closing


# Define Entry Schema
DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""
INSERT_ENTRY = """
INSERT INTO entries (title, text, created) VALUES (%s, %s, %s)
"""

DB_ENTRIES_LIST = """
SELECT id, title, text, created FROM entries ORDER BY created DESC
"""

logging.basicConfig()
log = logging.getLogger(__file__)

# @view_config(route_name='home', renderer='string')
# def home(request):
#     return 'Ey gurl'

def connect_db(settings):
    '''Return a connection to the configured database'''
    return psycopg2.connect(settings['db'])

@view_config(route_name='home', renderer='templates/list.jinja2')
def read_entries(request):
    '''Return a list of entries'''
    cur = request.db.cursor()
    cur.execute(DB_ENTRIES_LIST)
    keys = ('id', 'title', 'text', 'created')
    entries = [dict(zip(keys, row)) for row in cur.fetchall()]
    return {'entries': entries }

def init_db():
    '''Create database tables defined by DB_SCHEMA'''
    settings = {}
    settings['db'] = os.environ.get(
        'DATABASE_URL', 'dbname=learning-journal user=Jacques'
    )
    with closing(connect_db(settings)) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()

@subscriber(NewRequest)
def open_connection(event):
    request = event.request
    settings = request.registry.settings
    request.db = connect_db(settings)
    request.add_finished_callback(close_connection)

def close_connection(request):
    '''Close the database connection for this request.'''
    db = getattr(request, 'db', None)
    if db is not None:
        if request.exception is not None:
            db.rollback()
        else:
            db.commit()
        request.db.close()

def write_entry(request):
    '''Write an entry to the database'''
    title = request.params.get('title', None)
    text = request.params.get('text', None)
    created = datetime.datetime.utcnow()
    request.db.cursor().execute(INSERT_ENTRY, [title, text, created])

def main():
    '''Create a configured wsgi app'''
    settings = {}
    settings['reload_all'] = os.environ.get('DEBUG', True)
    settings['debug_all'] = os.environ.get('DEBUG', True)
    settings['db'] = os.environ.get(
        'DATABASE_URL', 'dbname=learning-journal user=Jacques'
    )
    # secret value for session signing
    secret = os.environ.get('JOURNAL_SESSION_SECRET', 'itsaseekrit')
    session_factory = SignedCookieSessionFactory(secret)
    # configuration setup
    config = Configurator(
        settings=settings,
        session_factory=session_factory
    )
    config.include('pyramid_jinja2')
    config.add_route('home', '/')
    config.scan()
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
