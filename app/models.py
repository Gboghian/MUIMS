from datetime import datetime, timezone
from datetime import datetime as utcnow
from sqlalchemy.sql import func
from . import db

# Association table for many-to-many relationship between incidents and parts
incident_parts = db.Table('incident_parts',
    db.Column('incident_id', db.Integer, db.ForeignKey('incident.id', ondelete='CASCADE'), nullable=False),
    db.Column('part_id', db.Integer, db.ForeignKey('part.id', ondelete='CASCADE'), nullable=False),
    db.UniqueConstraint('incident_id', 'part_id')
)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow.utcnow, nullable=False)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # basics
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)

    # client-requested fields
    customer_name = db.Column(db.String(100))      # "Customer Name"
    site_name = db.Column(db.String(150))          # "Site/Facility Name"
    location = db.Column(db.String(100))           # "Location"
    machine_model = db.Column(db.String(150))      # rename of Equipment -> Machine Model
    machine_serial = db.Column(db.String(150))     # "Machine Serial Number"
    fault = db.Column(db.String(255))              # "Fault"
    fault_code = db.Column(db.String(20))          # "Fault Code"
    start_time = db.Column(db.DateTime(timezone=True))            # "Start Time"
    end_time = db.Column(db.DateTime(timezone=True))              # "End Time"
    preventive_maintenance = db.Column(db.Boolean, default=False)
    parts_used = db.Column(db.Text, nullable=True)

    # classification
    category = db.Column(db.String(50), default="mechanical")
    severity = db.Column(db.String(20), default="Medium")
    status = db.Column(db.String(20), default="Open")

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    parts = db.relationship("Part", secondary=incident_parts, backref=db.backref("incidents", lazy="dynamic"), lazy="selectin")

    @property
    def duration_minutes(self):
        """Return duration in whole minutes, or None if not computable."""
        if not self.start_time:
            return None
        
        # Handle timezone-aware and naive datetime comparisons
        start = self.start_time.replace(tzinfo=timezone.utc) if self.start_time and self.start_time.tzinfo is None else self.start_time
        end = (self.end_time or datetime.now(timezone.utc))
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        
        # Guard invalid order
        if end < start:
            return None
        
        delta = end - start
        return int(delta.total_seconds() // 60)

    def human_duration(self):
        """Return nice text like '48m', '2h 15m', or 'N/A'."""
        mins = self.duration_minutes
        if mins is None:
            return "N/A"
        if mins < 60:
            return f"{mins}m"
        h, m = divmod(mins, 60)
        return f"{h}h {m}m" if m else f"{h}h"
