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
    title = TextField('Title', validators = [Required("Please enter title.")],
                      filters=[strip_filter])
    body = TextAreaField('Body', validators = [Required("Please enter body.")],
                         filters=[strip_filter])

    def __init__(self, original_title, original_body, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_title = original_title
        self.original_body = original_body

    def validate(self):
        if not Form.validate(self):
            return False
        if self.title.data == self.original_title:
            return True
        if self.body.data == self.original_body:
            return True
        return True