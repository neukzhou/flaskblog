from flask.ext.wtf import Form
from wtforms import TextField, validators, TextAreaField, BooleanField
from wtforms.validators import Required, Length
from app.models import User
 
strip_filter = lambda x: x.strip() if x else None
 
class PostCreateForm(Form):
    title = TextField('Title', validators = [Required("Please enter title.")],
                      filters=[strip_filter])
    body = TextAreaField('Body', validators = [Required("Please enter body.")],
                         filters=[strip_filter])


class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname = self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True