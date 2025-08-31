from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

SEVERITY_CHOICES = [("Low","Low"), ("Medium","Medium"), ("High","High")]
CATEGORY_CHOICES = [("mechanical","Mechanical"), ("electrical","Electrical"), ("software","Software")]
STATUS_CHOICES = [("Open","Open"), ("In Progress","In Progress"), ("Resolved","Resolved")]

def get_rounded_now():
    """Get current datetime rounded to the nearest minute"""
    now = datetime.now()
    return now.replace(second=0, microsecond=0)

class IncidentForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Detailed Description")

    customer_name = SelectField("Customer Name", choices=[], validators=[DataRequired()])
    site_name = SelectField("Site/Facility", choices=[], validators=[Optional()])
    location = SelectField("Location", choices=[], validators=[Optional()])
    machine_model = SelectField("Machine Model", choices=[], validators=[Optional()])
    machine_serial = SelectField("Machine Serial Number", choices=[], validators=[Optional()])

    fault_code = SelectField("Fault Code", choices=[], validators=[Optional()])
    fault = SelectField("Fault Description", choices=[], validators=[Optional()])

    start_time = DateTimeLocalField("Fault Start Time", format="%Y-%m-%dT%H:%M", validators=[Optional()], default=get_rounded_now)
    end_time   = DateTimeLocalField("Fault End Time",   format="%Y-%m-%dT%H:%M", validators=[Optional()])
    preventive_maintenance = BooleanField("Preventive Maintenance Related")

    category = SelectField("Category", choices=CATEGORY_CHOICES)
    severity = SelectField("Severity", choices=SEVERITY_CHOICES)
    status = SelectField("Status", choices=STATUS_CHOICES, default="Open")

    submit = SubmitField("Report Incident")

    def validate(self, **kwargs):
        ok = super().validate(**kwargs)
        if ok and self.start_time.data and self.end_time.data:
            if self.end_time.data < self.start_time.data:
                self.end_time.errors.append("End time cannot be before start time.")
                return False
        return ok

class FilterForm(FlaskForm):
    q = StringField("Search", validators=[Optional()], render_kw={"placeholder": "Search title or description..."})
    customer = SelectField("Customer", choices=[("", "All Customers")], validators=[Optional()])
    severity = SelectField("Severity", choices=[("", "All Severities")] + SEVERITY_CHOICES, validators=[Optional()])
    status = SelectField("Status", choices=[("", "All Statuses")] + STATUS_CHOICES, validators=[Optional()])
    date_from = DateTimeLocalField("From Date", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    date_to = DateTimeLocalField("To Date", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    
    submit = SubmitField("Filter")
    clear = SubmitField("Clear Filters")
