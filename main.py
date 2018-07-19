import datetime
import json
import webapp2

from google.appengine.api import memcache
from google.appengine.api import users


class GetLoginUrlHandler(webapp2.RequestHandler):
    def dispatch(self):
        result = {
            'url': users.create_login_url('/')
        }
        send_json(self, result)


def send_json(request_handler, props):
    request_handler.response.content_type = 'application/json'
    request_handler.response.out.write(json.dumps(props))



class GetLogoutUrlHandler(webapp2.RequestHandler):
    def dispatch(self):
        result = {
            'url': users.create_logout_url('/')
        }
        send_json(self, result)



class GetUserHandler(webapp2.RequestHandler):
    def dispatch(self):
        email = get_current_user_email()
        result = {}
        if email:
            result['user'] = email
        else:
            result['error'] = 'User is not logged in.'
        send_json(self, result)


def get_current_user_email():
    current_user = users.get_current_user()
    if current_user:
        return current_user.email()
    else:
        return None

#    ('/', GetUserHandler),
#    ('/user', GetUserHandler),


class AddMessageHandler(webapp2.RequestHandler):
    def dispatch(self):
        result = {}
        email = get_current_user_email()
        if email:
            msg_text = self.request.get('text')
            if len(msg_text) > 500:
                result['error'] = 'Message is too long.'
            else:
                messages = memcache.get('messages')
                if not messages:
                    messages = []
                msg = Message(email, msg_text)
                messages.append(msg)
                memcache.set('messages', messages)
                result['OK'] = True
        else:
            result['error'] = 'User is not logged in.'
        send_json(self, result)



class GetMessagesHandler(webapp2.RequestHandler):
    def dispatch(self):
        result = {}
        email = get_current_user_email()
        if email:
            result['messages'] = []
            messages = memcache.get('messages')
            if messages:
                for message in messages:
                    result['messages'].append(message.to_dict())
        else:
            result['error'] = 'User is not logged in.'
        send_json(self, result)
# add this mapping to your app
#     ('/messages', GetMessagesHandler),


class Message(object):
    def __init__(self, email, text):
        self.email = email
        self.text = text
        self.timestamp = datetime.datetime.now()
    def to_dict(self):
        result = {
            'email': self.email,
            'text': self.text,
            'time': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        return result




app = webapp2.WSGIApplication([
    ('/', GetUserHandler),
    ('/user', GetUserHandler),
    ('/login', GetLoginUrlHandler),
    ('/logout', GetLogoutUrlHandler),
    ('/add', AddMessageHandler),
    ('/messages', GetMessagesHandler),
], debug=True)
