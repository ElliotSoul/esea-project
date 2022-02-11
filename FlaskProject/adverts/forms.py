from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, DecimalField, RadioField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, NumberRange, ValidationError, Length
from collections import Counter

class AdvertForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=20)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=200, message="Max of 200 Characters")])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0.01, max=99999.99, message="That number is Invalid")])
    picture =FileField('Advert Photo', validators=[FileAllowed(['jpg', 'png'])])
    manufacturer = RadioField('Choose Which Manufacturer', choices=[('Intel', 'Intel'),('AMD', 'AMD'),('Asus', 'Asus'),('MSI', 'MSI'),('Gigabyte', 'Gigabyte'),('EVGA', 'EVGA'),('Zotac', 'Zotac'),('Nvidia', 'Nvidia'),('Other', 'Other')], validators=[DataRequired(message="Please Select a Manufacturer")])
    product = RadioField('Choose Which Product', choices=[('Motherboard', 'Motherboard'),('RAM', 'RAM'),('CPU', 'CPU'),('GPU', 'GPU'),('PSU', 'PSU'),('Case', 'Case'),('Prebuilt', 'Prebuilt'),('Other', 'Other')], validators=[DataRequired(message="Please Select a Product")])
    bid=BooleanField('Bid?')
    submit = SubmitField('Post Advert')

    def validate_content(self, content):
        temp=""
        enterval=0
        contentstring=content.data
        for i in range(0, len(str(content))):
            temp=temp+contentstring[:1]
            contentstring=contentstring[1:]
            if temp[len(temp)-1:] == " ":
                temp=""
            if len(temp)>35:
                raise ValidationError("One of Those Words are Invalid (One Word is too Long, Include a space)")
        enterval=Counter(temp)
        if enterval['\n']>3:
            raise ValidationError("Reduce 'Enter' Characters")

class EmailForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=200, message="Max of 200 Characters")])
    submit = SubmitField('Send Email')

    def validate_message(self, message):
        temp=""
        enterval=0
        contentstring=message.data
        for i in range(0, len(str(message))):
            temp=temp+contentstring[:1]
            contentstring=contentstring[1:]
            if temp[len(temp)-1:] == "\n":
                enterval=enterval+1
            if temp[len(temp)-1:] == " ":
                temp=""
            if len(temp)>35:
                raise ValidationError("One of Those Words are Invalid (One Word is too Long, Include a space)")
            if enterval>3:
                raise ValidationError("Reduce 'Enter' Characters")

class BidForm(FlaskForm):
    bid  = DecimalField('Enter your Bid', validators=[DataRequired(), NumberRange(min=0.01, max=99999.99, message="That number is Invalid")])
    submit = SubmitField('Send Bid')

