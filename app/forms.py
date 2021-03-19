from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtfforms.validators import DataRequired

class NotificationForm(FlaskForm):
    twitch_username = StringField('Twitch Username', validators=[DataRequired()])
    submit = SubmitField('Add Notification to Channel')

class DeleteNotificationForm(FlaskForm):
    twitch_username = StringField('Twitch Username', validators=[DataRequired()])
    submit = SubmitField('Delete Notification')