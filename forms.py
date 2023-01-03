from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FieldList, FormField, TextAreaField
from wtforms.validators import DataRequired, URL, InputRequired, Optional, Length


# Create WTForm
class LinkForm(FlaskForm):
    label = StringField("Label",
                        validators=[Optional(), Length(min=3, message='Input must be at least 5 characters long.')],
                        render_kw={'title': 'Enter a value with at least 5 characters',
                                   'placeholder': 'The label of your Url'})
    url = StringField("Url",
                      validators=[Optional(), URL(message='Input must be a valid URL.')],
                      render_kw={'title': 'Do not forget the HTTP/HTTPS',
                                 'placeholder': 'Your Url goes here.'}
                      )


class AdminForm(FlaskForm):
    bio = TextAreaField("Bio",
                        validators=[DataRequired()],
                        render_kw={'title': 'Write about yourself',
                                   'placeholder': 'Tell other people who are you and what you can do'}
                        )
    links = FieldList(FormField(LinkForm))
    submit = SubmitField("Save")
