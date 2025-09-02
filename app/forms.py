from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SelectMultipleField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

SEVERITY_CHOICES = [("Low","Low"), ("Medium","Medium"), ("High","High")]
CATEGORY_CHOICES = [("mechanical","Mechanical"), ("electrical","Electrical"), ("software","Software")]
STATUS_CHOICES = [("Open","Open"), ("In Progress","In Progress"), ("Resolved","Resolved")]

# Parts drop-down options (value, label)
PART_CHOICES = [
    ('water-cooling-system', 'Water Cooling System'),
    ('moveable-cabinet', 'Moveable Cabinet'),
    ('fixed-cabinet', 'Fixed Cabinet'),
    ('external-cable-sheets', 'External Cable Sheets'),
    ('exhaust-fan', 'Exhaust Fan'),
    ('rack-cooling-fan', 'Rack Cooling Fan'),
    ('6kva-ups', '6KVA UPS'),
    ('floor-leveling-bolt', 'Floor Leveling Bolt'),
    ('machine-caster', 'Machine Caster'),
    ('monitor', 'Monitor'),
    ('power-supply-12v-5v', 'Power Supply 12V & 5V'),
    ('ups-12-volt-battery', 'UPS 12 Volt Battery'),
    ('machine-power-cable', 'Machine Power Cable'),
    ('ups-power-cable', 'UPS Power Cable'),
    ('lan-cable', 'LAN Cable'),
    ('monitor-power-cable', 'Monitor Power Cable'),
    ('monitor-hdmi-cable', 'Monitor HDMI Cable'),
    ('machine-cable-tray', 'Machine Cable Tray'),
    ('screw-bolt-nut', 'Screw, Bolt & Nut'),
    ('belt-2m-with-plastic-blocks', 'Belt 2M With Plastic Blocks'),
    ('green-belt', 'Green Belt'),
    ('green-belt-tensioner', 'Green Belt Tensioner'),
    ('turntable-belt', 'Turntable Belt'),
    ('tutto-screw-belt-4', 'TUTTO Screw Belt 4'),
    ('tutto-screw-belt-5', 'TUTTO Screw Belt 5'),
    ('drivers-motor-roller', 'Drivers Motor Roller'),
    ('roller-19-inch', 'Roller 19 Inch'),
    ('idler-sprocket', 'Idler Sprocket'),
    ('drive-sprocket', 'Drive Sprocket'),
    ('turntable-drive-roller', 'Turntable Drive Roller'),
    ('3-way-direction-gear-3025', '3-Way Direction Gear 3025'),
    ('3-way-direction-gear-3036', '3-Way Direction Gear 3036'),
    ('shaft-gear-with-2-bearing', 'Shaft Gear With 2 Bearing'),
    ('gear-motor', 'Gear Motor'),
    ('turntable-gear', 'Turntable Gear'),
    ('turntable-fixed-gear', 'Turntable Fixed Gear'),
    ('turntable-joint-bracket', 'Turntable Joint Bracket'),
    ('turntable-vertical-shaft', 'Turntable Vertical Shaft'),
    ('turntable-bevel-gear', 'Turntable Bevel Gear'),
    ('turntable-bearing', 'Turntable Bearing'),
    ('turntable-vertical-bearing', 'Turntable Vertical Bearing'),
    ('turntable-vertical-bevel-gear', 'Turntable Vertical Bevel Gear'),
    ('pneumatic-hose-pu-6mm', 'Pneumatic Hose PU 6mm'),
    ('pneumatic-fitting-straight', 'Pneumatic Fitting Straight'),
    ('pneumatic-fitting-elbow', 'Pneumatic Fitting Elbow'),
    ('pneumatic-fitting-tee', 'Pneumatic Fitting Tee'),
    ('pneumatic-connector-6mm', 'Pneumatic Connector 6mm'),
    ('pneumatic-y-connector', 'Pneumatic Y Connector'),
    ('pneumatic-hose-8mm', 'Pneumatic Hose 8mm'),
    ('pneumatic-fitting-8mm', 'Pneumatic Fitting 8mm'),
    ('pneumatic-connector-8mm', 'Pneumatic Connector 8mm'),
    ('pneumatic-big-tee-8mm', 'Pneumatic Big Tee 8mm'),
    ('solenoid-valve-2way', 'Solenoid Valve 2Way'),
    ('solenoid-valve-2-way-with-diodes', 'Solenoid Valve 2 Way with Diodes'),
    ('solenoid-valve-3way', 'Solenoid Valve 3Way'),
    ('solenoid-valve-5way', 'Solenoid Valve 5Way'),
    ('pneumatic-cylinder-8mm', 'Pneumatic Cylinder 8mm'),
    ('pneumatic-cylinder-16mm', 'Pneumatic Cylinder 16mm'),
    ('pneumatic-cylinder-20mm', 'Pneumatic Cylinder 20mm'),
    ('pneumatic-cylinder-25mm', 'Pneumatic Cylinder 25mm'),
    ('pneumatic-cylinder-32mm', 'Pneumatic Cylinder 32mm'),
    ('pneumatic-cylinder-40mm', 'Pneumatic Cylinder 40mm'),
    ('pneumatic-cylinder-50mm', 'Pneumatic Cylinder 50mm'),
    ('pneumatic-cylinder-63mm', 'Pneumatic Cylinder 63mm'),
    ('pneumatic-cylinder-80mm', 'Pneumatic Cylinder 80mm'),
    ('pneumatic-cylinder-100mm', 'Pneumatic Cylinder 100mm'),
    ('pneumatic-pressure-control-valve', 'Pneumatic Pressure Control Valve'),
    ('pneumatic-flow-control-valve', 'Pneumatic Flow Control Valve'),
    ('pneumatic-check-valve', 'Pneumatic Check Valve'),
    ('pneumatic-exhaust-control-valve', 'Pneumatic Exhaust Control Valve'),
    ('pneumatic-quick-exhaust-valve', 'Pneumatic Quick Exhaust Valve'),
    ('pneumatic-quick-coupler', 'Pneumatic Quick Coupler'),
    ('pneumatic-quick-coupler-cap', 'Pneumatic Quick Coupler Cap'),
    ('pneumatic-hose-clamp', 'Pneumatic Hose Clamp'),
    ('pneumatic-lubricator', 'Pneumatic Lubricator'),
    ('pneumatic-connector-1-4', 'Pneumatic Connector 1/4'),
    ('pneumatic-connector-3-8', 'Pneumatic Connector 3/8'),
    ('pneumatic-connector-1-2', 'Pneumatic Connector 1/2'),
    ('pneumatic-connector-3-4', 'Pneumatic Connector 3/4'),
    ('pneumatic-connector-1-inch', 'Pneumatic Connector 1 Inch'),
    ('air-pressure-gauge', 'Air Pressure Gauge'),
    ('pneumatic-oil', 'Pneumatic Oil'),
    ('air-filter', 'Air Filter'),
    ('regulator', 'Regulator'),
    ('lubricator', 'Lubricator'),
    ('festo-sensor-4mm', 'FESTO Sensor 4mm'),
    ('festo-sensor-6mm', 'FESTO Sensor 6mm'),
    ('festo-sensor-8mm', 'FESTO Sensor 8mm'),
    ('auto-drain-valve', 'Auto Drain Valve'),
    ('actuator', 'Actuator'),
    ('air-compressor', 'Air Compressor'),
    ('air-compressor-oil', 'Air Compressor Oil'),
    ('safety-valve', 'Safety Valve'),
    ('non-return-valve', 'Non-Return Valve'),
    ('manifold', 'Manifold'),
    ('silencer', 'Silencer'),
    ('air-dryer', 'Air Dryer'),
    ('air-receiver-tank', 'Air Receiver Tank'),
    ('bearing-608zz', 'Bearing 608ZZ'),
    ('bearing-6202', 'Bearing 6202'),
    ('bearing-6203', 'Bearing 6203'),
    ('bearing-6204', 'Bearing 6204'),
    ('bearing-6205', 'Bearing 6205'),
    ('bearing-6206', 'Bearing 6206'),
    ('bearing-6207', 'Bearing 6207'),
    ('bearing-6208', 'Bearing 6208'),
    ('bearing-6209', 'Bearing 6209'),
    ('bearing-6210', 'Bearing 6210'),
    ('bearing-6211', 'Bearing 6211'),
    ('bearing-6212', 'Bearing 6212'),
    ('bearing-6213', 'Bearing 6213'),
    ('bearing-6214', 'Bearing 6214'),
    ('bearing-6215', 'Bearing 6215'),
    ('bearing-6216', 'Bearing 6216'),
    ('bearing-6217', 'Bearing 6217'),
    ('bearing-6218', 'Bearing 6218'),
    ('bearing-6219', 'Bearing 6219'),
    ('bearing-6220', 'Bearing 6220'),
    ('bearing-6302', 'Bearing 6302'),
    ('bearing-6303', 'Bearing 6303'),
    ('bearing-6304', 'Bearing 6304'),
    ('bearing-6305', 'Bearing 6305'),
    ('bearing-6306', 'Bearing 6306'),
    ('bearing-6307', 'Bearing 6307'),
    ('bearing-6308', 'Bearing 6308'),
    ('bearing-6309', 'Bearing 6309'),
    ('bearing-6310', 'Bearing 6310'),
]

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
    parts_used = SelectMultipleField('Parts Used', choices=[], coerce=str, validate_choice=False, render_kw={"id": "parts_used"})
    parts_other = StringField('Other Parts (optional)')

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
