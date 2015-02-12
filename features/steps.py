import datetime
import os
from lettuce import before, after, world, step
from contextlib import closing
from pyramid import testing
from journal import DB_SCHEMA, INSERT_ENTRY, connect_db

# TODO:
# Pull database credentials from environment
# Connect to the database
# Define HTML structures for test values, ie:
# ADD_BUTTON = '<input type='submit.....



# via http://lettuce.it/reference/terrain.html#lettuce-world-absorb
@world.absorb
def create_entry():
    data = {
        'title': 'Post title',
        'content': 'Post content'
    }
    # return app.get(<ADD ROUTE>, params=data, status='3*')

@world.absorb
def login(username, password, app):
    credentials = {
        'username': username,
        'password': password
    }
    # return app.post(<LOGIN ROUTE>, params=credentials, status='*')



@before.all
def init_db():
    with closing(connect_db(settings)) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()

@after.all
def drop_db():
    with closing(connect_db(settings)) as db:
        db.cursor().execute("DROP TABLE entries")
        db.commit()



@before.each_scenario
def app(scenario):
    from journal import main
    from webtest import TestApp
    os.environ['DATABASE_URL'] = TEST_DSN
    app = main()
    world.test_app = TestApp(app)

@after.each_scenario
def clear(scenario):
    with closing(connect_db(settings)) as db:
        db.cursor().execute('DELETE FROM entries')
        db.commit()



# From here, we can begin defining our steps
# Cool beans.
