from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired

class HomeFilter(FlaskForm):
    manufacturer = RadioField('Choose Which Manufacturer', choices=[('Intel', 'Intel'),('AMD', 'AMD'),('Asus', 'Asus'),('MSI', 'MSI'),('Gigabyte', 'Gigabyte'),('EVGA', 'EVGA'),('Zotac', 'Zotac'),('Nvidia', 'Nvidia'),('Other', 'Other')])
    product = RadioField('Choose Which Product', choices=[('Motherboard', 'Motherboard'),('RAM', 'RAM'),('CPU', 'CPU'),('GPU', 'GPU'),('PSU', 'PSU'),('Case', 'Case'),('Prebuilt', 'Prebuilt'),('Other', 'Other')])
    sort = RadioField('Sort By', choices=[("date_posted.desc()", 'Newest'),("date_posted.asc()", 'Oldest'),("price.desc()", 'Price Low-High'),("price.asc()", 'Price High-Low')], default="date_posted.desc()")
    submit = SubmitField('Filter')