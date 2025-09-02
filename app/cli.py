from . import db
from .models import Incident, Part
from datetime import datetime, timedelta

def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        db.drop_all(); db.create_all()
        print("DB reset.")

    @app.cli.command("seed")
    def seed():
        # Clear existing incidents
        Incident.query.delete()
        
        now = datetime.utcnow()
        
        # Demo incident 1: Resolved mechanical issue
        incident1 = Incident(
            title="Conveyor Belt Malfunction",
            description="Main conveyor belt stopped unexpectedly.\nUnusual grinding noises reported before shutdown.\nMaintenance team investigated motor assembly.",
            customer_name="VLTX",
            site_name="Birmingham",
            location="United Kingdom",
            machine_model="7000",
            machine_serial="7000-001",
            fault="Motor bearing failure detected\nOverheating symptoms observed",
            fault_code="E1001",
            start_time=now - timedelta(days=2, hours=8),
            end_time=now - timedelta(days=2, hours=6, minutes=30),
            category="mechanical",
            severity="High",
            status="Resolved"
        )
        
        # Demo incident 2: Open electrical issue
        incident2 = Incident(
            title="Server Rack Power Alert",
            description="Critical power supply fault in Server Rack B.\nMultiple servers showing unstable power readings.",
            customer_name="Bol",
            site_name="Belfast",
            location="United Kingdom",
            machine_model="7000",
            machine_serial="7000-042",
            fault="Primary power rail voltage drop\nBackup PSU not engaging automatically",
            fault_code="E2205",
            start_time=now - timedelta(hours=4),
            end_time=None,
            category="electrical",
            severity="High",
            status="Open"
        )
        
        # Demo incident 3: In Progress software issue
        incident3 = Incident(
            title="PLC Programming Error",
            description="Assembly line control system showing erratic behavior.\nRandom stops and starts affecting production schedule.",
            customer_name="Bank Muscat",
            site_name="Muscat",
            location="Oman",
            machine_model="V-Series",
            machine_serial="V-Series-789",
            fault="Logic error in cycle timing routine\nSensor input validation failing",
            fault_code="S0156",
            start_time=now - timedelta(hours=6, minutes=20),
            end_time=None,
            category="software",
            severity="Medium",
            status="In Progress"
        )
        
        # Demo incident 4: Resolved low priority
        incident4 = Incident(
            title="Cooling Fan Noise",
            description="Unusual noise from cooling fan unit.\nNo performance impact observed yet.",
            customer_name="TransG",
            site_name="Dubai",
            location="UAE",
            machine_model="7000",
            machine_serial="7000-156",
            fault="Fan bearing wear causing vibration noise",
            fault_code="F0301",
            start_time=now - timedelta(days=1, hours=3),
            end_time=now - timedelta(days=1, hours=2, minutes=45),
            category="mechanical",
            severity="Low",
            status="Resolved"
        )
        
        # Demo incident 5: Open preventive maintenance
        incident5 = Incident(
            title="Scheduled Hydraulic System Check",
            description="Routine preventive maintenance check revealed potential issues.\nHydraulic pressure slightly below optimal range.",
            customer_name="VLTX",
            site_name="London Kings Cross",
            location="United Kingdom",
            machine_model="Cobra",
            machine_serial="Cobra-023",
            fault="Hydraulic fluid pressure 5% below specification\nMinor seal wear detected",
            fault_code="H1205",
            start_time=now - timedelta(minutes=30),
            end_time=None,
            preventive_maintenance=True,
            category="mechanical",
            severity="Medium",
            status="Open"
        )
        
        # Add all incidents to session
        incidents = [incident1, incident2, incident3, incident4, incident5]
        for incident in incidents:
            db.session.add(incident)
        
        db.session.commit()
        print(f"Seeded {len(incidents)} demo incidents with mixed severities and statuses.")

    @app.cli.command("seed-parts")
    def seed_parts():
        import os
        path = os.path.join(os.path.dirname(__file__), "data", "parts.txt")
        if not os.path.exists(path):
            print("No parts file found:", path)
            return
        added = 0
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                name = raw.strip()
                if not name:
                    continue
                exists = Part.query.filter(db.func.lower(Part.name) == name.lower()).first()
                if not exists:
                    db.session.add(Part(name=name))
                    added += 1
        db.session.commit()
        print(f"Seeded {added} parts.")
