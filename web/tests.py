'''
Run the tests using testrunner.py script in the project root directory.

Usage: testrunner.py SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules

Options:
  -h, --help  show this help message and exit

'''
import unittest
import os

import webapp2
import webtest
from google.appengine.ext import testbed
from mock import Mock

import bp_content
from bp_content.themes.default import config as config_theme
from bp_includes import config as config_boilerplate
from bp_content.themes.default import routes as routes_theme
from bp_includes import routes as routes_boilerplate
from bp_includes.lib import utils
from bp_includes.lib import i18n
from bp_includes.lib import test_helpers


# setting HTTP_HOST in extra_environ parameter for TestApp is not enough for TaskQueue stub
os.environ['HTTP_HOST'] = 'localhost'

# globals
network = False

# mock Internet calls
if not network:
    i18n.get_territory_from_ip = Mock(return_value=None)


class AppTest(unittest.TestCase, test_helpers.HandlerHelpers):
    def setUp(self):

        # create a WSGI application.
        webapp2_config = config_boilerplate.config
        webapp2_config.update(config_theme.config)
        self.app = webapp2.WSGIApplication(config=webapp2_config)
        routes_theme.add_routes(self.app)
        routes_boilerplate.add_routes(self.app)
        self.testapp = webtest.TestApp(self.app, extra_environ={'REMOTE_ADDR' : '127.0.0.1'})
        
        # use absolute path for templates
        self.app.config['webapp2_extras.jinja2']['template_path'] =  [os.path.join(os.path.dirname(bp_content.__file__), '../templates'), os.path.join(os.path.dirname(bp_content.__file__), 'templates')]

        # activate GAE stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_taskqueue_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.testbed.init_user_stub()

        self.headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) Version/6.0 Safari/536.25',
                        'Accept-Language' : 'en_US'}

        # fix configuration if this is still a raw boilerplate code - required by test with mails
        if not utils.is_email_valid(self.app.config.get('contact_sender')):
            self.app.config['contact_sender'] = "noreply-testapp@example.com"
        if not utils.is_email_valid(self.app.config.get('contact_recipient')):
            self.app.config['contact_recipient'] = "support-testapp@example.com"

    def tearDown(self):
        self.testbed.deactivate()

    def test_config_environment(self):
        self.assertEquals(self.app.config.get('environment'), 'testing')

class ModelTest(unittest.TestCase):
    def setUp(self):

        # activate GAE stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    unittest.main()
