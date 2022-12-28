from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FieldList, FormField, TextAreaField
from wtforms.validators import DataRequired, URL


# Create WTForm
class LinkForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    url = StringField(validators=[DataRequired()])


class AdminForm(FlaskForm):
    bio = TextAreaField("Bio", validators=[DataRequired()])
    links = FieldList(FormField(LinkForm))
    submit = SubmitField("Save", validators=[DataRequired()])
