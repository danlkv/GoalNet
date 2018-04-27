from StateMachine import States
from frm import handles as h
from DataBase import db

ps =h.post
a = h.action

def contact_check(i,s,d,role=None):
    c= i.contact
    # check if user sent his own contact
    if i.from_user.id ==c.user_id:
        # database call
        if db.user_registered(c.phone_number):
            db.add_chat_id(c.phone_number,c.user_id)
            d['role']='student'
            if db.user_gmail(c.user_id):
                new_state = States.HOME
            else:
                new_state=States.GMAIL
        else:
            if d.get('role')=='applicant':
                # set applicant info
                d['phone'] = c.phone_number
                d['tgchat'] = c.user_id
                new_state =States.GMAIL
            else:
                new_state=States.NOT_ENROLLED
    else:
        new_state = States.TG_ERR
    return new_state, d

login_kb= [
    {'Send contact':a(contact_check,react_to='contact'),
     'kwargs':{'request_contact':True}},
    {'<- Back':a(States.START)}
]

def set_name(i,s,**d):
    d['name'] = i.from_user.first_name
    return d
def save_gmail(i,d,name=None,role=None):
    if role:
        if role=='applicant':
            # finish application process
            data = {'firstname':d['fname'],
                    'lastname':d['lname'],
                    'phone':d['phone'],
                    'tgchat':i.from_user.id,
                    'email':i.text
                   }
            db.save_new_user(data)
            # now send notification to admins
            new_state = States.USER_SAVED
        else:
            new_state = States.HOME
            print('saving gmail addr')
            db.save_gmail(i.text,i.from_user.id)
    else:
        new_state = States.ERROR
        db.save_gmail(i.text,i.from_user.id)
    return new_state,{'role':role}

UI={
    States.START:{'t':
        h.st(
      ("Hey %s, nice to meet you! "
       "I'm Aristotle, and I will help you at Fless. "
           "What would you like to do?"), 'name'),
          'b':[{'Log in as student':a(States.TG)},

               {'Explore Fless':a(States.ALL_COURSES)}
              ],
                'prepare':set_name,
      },
    States.TG:{'t':
               h.st(
          ("%s, Please share your contact details"
           "so I can recognize you"),'name'),
               'kb':h.obj(login_kb)
              },

    States.TG_ERR:{'t':
                   h.st(
          ("%s, I'm afraid this is not your contact. "
           "Please share your contact"),'name'),
               'kb':h.obj(login_kb)
      },
    States.GMAIL:{'t':
          h.st("%s, Please share your email address",
              'name'),
                  'react':a(save_gmail,react_to='text'),
                  'kb':'Remove'
      },

    States.NOT_ENROLLED:{'t':
         ("It seems that you are "
          "not currently enrolled in any of"
          "the courses. Would you like to enrol "
          "now? Or contact Fless if you think "
          "here was a mistake"),
                         'b':[
         {'List Fless courses':a(States.ALL_COURSES)},
         {'Contact':a(States.CONTACT)}
                         ]
                        }
}
