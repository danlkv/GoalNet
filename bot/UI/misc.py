from StateMachine import States
from frm import handles as h
from frm.coffee_ui import CoffeeUI
from DataBase import db
import config

ps =h.post
a = h.action

UI={
    States.CONTACT:{'t':
                    ("Tell me what's on your mind, and I'll pass it over to"
                     "the rest of Fless team. We'll get back to you shortly"),
                    'b':[{"To start":a(States.START)}],
                    'react':a(States.CONTACT_THANKS,react_to='text')
      },
    States.USER_SAVED:{'t':
          "Sucess! We will contact you",
                       'b':[{'To start':a(lambda i,s,**d:\
                                          (States.START,dict(d,role=None)))}]
      },
    States.ERROR:{'t':
          ("Sorry, an error occured."
           "Please contact us on %s"%config.error_contact),
          'b':[{'To start':a(States.START)}]
      },
}
thankyou = CoffeeUI("""
                   CONTACT_THANKS:
                       t:'Thank you for your question, we will get to you shortly'
                       b:['To start':a 'START']
                   """,States)
th = thankyou.get_ui()
UI.update(th)
print(th)
