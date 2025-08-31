from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response
import json
import csv
import io
from . import db
from .models import Incident
from .forms import IncidentForm, FilterForm

main = Blueprint("main", __name__)

@main.route("/", endpoint="index")
def index():
    recent_incidents = (
        Incident.query
        .order_by(Incident.created_at.desc())
        .limit(5)
        .all()
    )
    total = Incident.query.count()
    open_ = Incident.query.filter_by(status="Open").count()
    high_count = Incident.query.filter_by(severity="High").count()
    return render_template("index.html", recent_incidents=recent_incidents, total=total, open_=open_, high_count=high_count)

@main.route("/incidents", endpoint="incidents")
def incidents():
    form = FilterForm()
    
    # Populate customer choices for the filter form
    customers = db.session.query(Incident.customer_name).distinct().filter(Incident.customer_name.isnot(None)).all()
    customer_choices = [("", "All Customers")] + [(c[0], c[0]) for c in customers if c[0]]
    form.customer.choices = customer_choices
    
    # Get query parameters and populate form
    q = request.args.get('q', '').strip()
    customer = request.args.get('customer', '')
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Pre-populate form with current filter values
    form.q.data = q
    form.customer.data = customer
    form.severity.data = severity
    form.status.data = status
    if date_from:
        try:
            from datetime import datetime
            form.date_from.data = datetime.fromisoformat(date_from.replace('T', ' '))
        except:
            pass
    if date_to:
        try:
            from datetime import datetime
            form.date_to.data = datetime.fromisoformat(date_to.replace('T', ' '))
        except:
            pass
    
    # Build query with filters
    query = Incident.query
    
    # Text search filter
    if q:
        query = query.filter(
            db.or_(
                Incident.title.icontains(q),
                Incident.description.icontains(q)
            )
        )
    
    # Customer filter
    if customer:
        query = query.filter(Incident.customer_name == customer)
    
    # Status filter
    if status:
        query = query.filter(Incident.status == status)
    
    # Severity filter - only filter if severity is one of the valid choices
    if severity and severity in ['Low', 'Medium', 'High']:
        query = query.filter(Incident.severity == severity)
    
    # Date range filters
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.fromisoformat(date_from.replace('T', ' '))
            query = query.filter(Incident.created_at >= date_from_obj)
        except:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.fromisoformat(date_to.replace('T', ' '))
            query = query.filter(Incident.created_at <= date_to_obj)
        except:
            pass
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Paginate the query
    pagination = query.order_by(Incident.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    items = pagination.items
    
    return render_template("incidents.html", 
                         items=items, 
                         pagination=pagination,
                         form=form,
                         q=q, 
                         customer=customer,
                         status=status, 
                         severity=severity,
                         date_from=date_from,
                         date_to=date_to)

@main.route("/incident/new", methods=["GET","POST"], endpoint="new_incident")
def new_incident():
    form = IncidentForm()

    # Customer mapping as specified
    customer_map = {
        "customers": ["VLTX", "Bol", "Bank Muscat", "TransG"],
        "sites": {
            "VLTX": ["Birmingham","London Kings Cross","Tonbridge","Bristol","Woolston","Kilmarnock","Washington"],
            "Bol": ["Belfast"],
            "Bank Muscat": ["Muscat"],
            "TransG": ["Dubai"]
        },
        "locations": {
            "VLTX": ["United Kingdom"],
            "Bol": ["United Kingdom"],
            "Bank Muscat": ["Oman"],
            "TransG": ["UAE"]
        },
        "models": {
            "VLTX": ["7000","V-Series","Cobra"],
            "Bol": ["7000"],
            "Bank Muscat": ["7000","V-Series"],
            "TransG": ["7000"]
        }
    }

    FAULT_MAP = {
        # code -> description
        "1CC": "Feedscan Module Card Cage",
        "1C":  "Feedscan Module Customer",
        "1D":  "Feedscan Module Detector Name",
        "1E":  "Feedscan Module Electrical",
        "1F":  "Feedscan Module Feeder",
        "1FO": "Feedscan Module Foreign Objects",
        "1M":  "Feedscan Module Mechanical",
        "8D":  "Miscellaneous DLR",
        "8C":  "Miscellaneous Valtex",
        "6D":  "Network System DLR",
        "6S":  "Network System SCM",
        "9FO": "PM (Foreign Object Found)",
        "10E":"Software Error Message",
        "3C": "Stacker Module Customer",
        "3E": "Stacker Module Electrical",
        "3FO":"Stacker Module Foreign Object",
        "3M": "Stacker Module Mechanical",
        "4E2":"Strapper Pocket Electrical",
        "4E3":"Strapper Pocket Electrical",
        "4E4":"Strapper Pocket Electrical",
        "4E6":"Strapper Pocket Electrical",
        "4E7":"Strapper Pocket Electrical",
        "4E8":"Strapper Pocket Electrical",
        "4E9":"Strapper Pocket Electrical",
        "4E10":"Strapper Pocket Electrical",
        "4E12":"Strapper Pocket Electrical",
        "4FO1":"Strapper Pocket Foreign Object",
        "4FO2":"Strapper Pocket Foreign Object",
        "4FO3":"Strapper Pocket Foreign Object",
        "4FO7":"Strapper Pocket Foreign Object",
        "4FO9":"Strapper Pocket Foreign Object",
        "4FO9B":"Strapper Pocket Foreign Object",
        "4F010":"Strapper Pocket Foreign Object",
        "4F011":"Strapper Pocket Foreign Object",
        "4M5":"Strapper Pocket Mechanical",
        "4M6":"Strapper Pocket Mechanical",
        "4M7":"Strapper Pocket Mechanical",
        "4M8":"Strapper Pocket Mechanical",
        "4M9":"Strapper Pocket Mechanical",
        "4P1":"Strapper Pocket Pneumatic",
        "4P10":"Strapper Pocket Pneumatic",
        "4P11":"Strapper Pocket Pneumatic",
        "4P12":"Strapper Pocket Pneumatic",
        "4P2":"Strapper Pocket Pneumatic",
        "4P3":"Strapper Pocket Pneumatic",
        "4P4":"Strapper Pocket Pneumatic",
        "4P5":"Strapper Pocket Pneumatic",
        "4P6":"Strapper Pocket Pneumatic",
        "4P9":"Strapper Pocket Pneumatic",
        "5A":"System Air",
        "5C":"System Customer",
        "5D":"System DLR",
        "5E":"System Electrical"
    }

    SITE_SERIAL_MAP = {
        "Birmingham": [
            ("BIRM27", "7000"),
            ("BIRM30", "7000"),
            ("BIRM35", "7000"),
            ("BIRMV01", "V-Series"),
            ("BIRMV01", "V-Series"),
            ("BIRMV05", "V-Series"),
            ("BIRMV05", "V-Series"),
        ],
        "Bristol": [
            ("BRIS28", "7000"),
            ("BRIS31", "7000"),
            ("BRISV02", "V-Series"),
        ],
        "Kilmarnock": [
            ("KILM105", "Cobra"),
            ("KILM29", "7000"),
            ("KILM33", "7000"),
        ],
        "London Kings Cross": [
            ("LOND24", "7000"),
            ("LOND32", "7000"),
        ]
        # Add more sites/rows here as needed
    }

    def serial_choices_for(site):
        pairs = SITE_SERIAL_MAP.get(site, [])
        return [(s, s) for (s, _m) in pairs]

    def model_for(site, serial):
        for s, m in SITE_SERIAL_MAP.get(site, []):
            if s == serial:
                return m
        return None

    # Always set customer choices so WTForms can validate it
    form.customer_name.choices = [(c, c) for c in customer_map["customers"]]

    # Always set fault_code choices (sorted by code)
    form.fault_code.choices = [("", "Select fault code...")] + [(k, k) for k in sorted(FAULT_MAP.keys())]
    # Fault description choices mirror the map values
    form.fault.choices = [("", "Select fault description...")] + [(v, v) for v in sorted(set(FAULT_MAP.values()))]

    # Ensure machine_model choices are at least present
    # We'll restrict via server guard and also set the final value from the mapping
    all_models = sorted({m for pairs in SITE_SERIAL_MAP.values() for (_s, m) in pairs})
    form.machine_model.choices = [("", "Select model...")] + [(m, m) for m in all_models]

    # If posting, populate dependent choices BEFORE validate_on_submit
    if request.method == "POST":
        c = request.form.get("customer_name", "")
        sites     = customer_map["sites"].get(c, [])
        locations = customer_map["locations"].get(c, [])
        models    = customer_map["models"].get(c, [])

        form.site_name.choices   = [(v, v) for v in sites]
        form.location.choices    = [(v, v) for v in locations]
        form.machine_model.choices = [(v, v) for v in models]

        # Build dependent choices for site-serial mapping BEFORE validate_on_submit
        posted_site = request.form.get("site_name", "")
        form.machine_serial.choices = [("", "Select serial...")] + serial_choices_for(posted_site)

        # Also ensure the submitted fault pair is valid before validate_on_submit
        posted_code = request.form.get("fault_code") or ""
        posted_desc = request.form.get("fault") or ""

        # Rebuild choices so WTForms validate_choice passes
        if posted_code and posted_code in FAULT_MAP:
            # Set description choices to include exactly the mapped description for the selected code
            mapped_desc = FAULT_MAP[posted_code]
            form.fault.choices = [("", "Select fault description..."), (mapped_desc, mapped_desc)]
        # else keep the generic list for GET or empty code

    if form.validate_on_submit():
        c = form.customer_name.data
        
        # (optional) extra guardrails for customer mapping
        if form.site_name.data and form.site_name.data not in customer_map["sites"].get(c, []):
            form.site_name.errors.append("Invalid site for selected customer.")
            return render_template("incident_form.html", form=form,
                                   customer_map=json.dumps(customer_map),
                                   fault_map=json.dumps(FAULT_MAP),
                                   site_serial_map=json.dumps(SITE_SERIAL_MAP))

        if form.location.data and form.location.data not in customer_map["locations"].get(c, []):
            form.location.errors.append("Invalid location for selected customer.")
            return render_template("incident_form.html", form=form,
                                   customer_map=json.dumps(customer_map),
                                   fault_map=json.dumps(FAULT_MAP),
                                   site_serial_map=json.dumps(SITE_SERIAL_MAP))

        if form.machine_model.data and form.machine_model.data not in customer_map["models"].get(c, []):
            form.machine_model.errors.append("Invalid machine model for selected customer.")
            return render_template("incident_form.html", form=form,
                                   customer_map=json.dumps(customer_map),
                                   fault_map=json.dumps(FAULT_MAP),
                                   site_serial_map=json.dumps(SITE_SERIAL_MAP))

        # Server guard: if a code is provided, description must match FAULT_MAP[code]
        if form.fault_code.data:
            expected = FAULT_MAP.get(form.fault_code.data)
            if not expected:
                form.fault_code.errors.append("Unknown fault code.")
                return render_template("incident_form.html", form=form,
                                       customer_map=json.dumps(customer_map),
                                       fault_map=json.dumps(FAULT_MAP),
                                       site_serial_map=json.dumps(SITE_SERIAL_MAP))
            if form.fault.data and form.fault.data != expected:
                form.fault.errors.append("Fault description doesn't match the selected code.")
                return render_template("incident_form.html", form=form,
                                       customer_map=json.dumps(customer_map),
                                       fault_map=json.dumps(FAULT_MAP),
                                       site_serial_map=json.dumps(SITE_SERIAL_MAP))

        # Site-serial validation
        site = form.site_name.data
        serial = form.machine_serial.data

        # If a serial is provided, it must belong to the selected site
        if serial:
            valid_serials = {s for (s, _m) in SITE_SERIAL_MAP.get(site, [])}
            if serial not in valid_serials:
                form.machine_serial.errors.append("Invalid serial for selected site.")
                return render_template("incident_form.html", form=form,
                                       customer_map=json.dumps(customer_map),
                                       fault_map=json.dumps(FAULT_MAP),
                                       site_serial_map=json.dumps(SITE_SERIAL_MAP))

            # Force the model to the one tied to this serial
            mapped_model = model_for(site, serial)
            form.machine_model.data = mapped_model
        
        # If validation passes, create the incident
        i = Incident(
            title=form.title.data,
            description=form.description.data,
            customer_name=form.customer_name.data,
            site_name=form.site_name.data,
            location=form.location.data,
            machine_model=form.machine_model.data,
            machine_serial=form.machine_serial.data,
            fault_code=form.fault_code.data or None,
            fault=form.fault.data or None,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            preventive_maintenance=form.preventive_maintenance.data,
            category=form.category.data,
            severity=form.severity.data,
            status=form.status.data,
        )
        db.session.add(i)
        db.session.commit()
        flash("✅ Incident submitted successfully.", "success")
        return redirect(url_for("main.incidents"))
    
    return render_template("incident_form.html", form=form,
                           customer_map=json.dumps(customer_map),
                           fault_map=json.dumps(FAULT_MAP),
                           site_serial_map=json.dumps(SITE_SERIAL_MAP))

@main.route("/incident/<int:incident_id>", endpoint="incident_detail")
def incident_detail(incident_id):
    i = Incident.query.get_or_404(incident_id)
    return render_template("incident_detail.html", i=i)

@main.route("/incident/<int:incident_id>/status", methods=["POST"], endpoint="incident_status")
def incident_status(incident_id):
    i = Incident.query.get_or_404(incident_id)
    new_status = request.form.get('status')
    if new_status in ['Open', 'In Progress', 'Resolved']:
        i.status = new_status
        db.session.commit()
        flash(f"✅ Incident #{i.id} status updated to {new_status}.", "success")
    return redirect(url_for("main.incidents"))

@main.route("/incident/<int:id>/start", methods=["POST"], endpoint="incident_start")
def incident_start(id):
    i = Incident.query.get_or_404(id)
    i.status = "In Progress"
    db.session.commit()
    flash(f"✅ Work started on incident #{i.id}.", "success")
    return redirect(url_for("main.incident_detail", incident_id=i.id))

@main.route("/incident/<int:id>/resolve", methods=["POST"], endpoint="incident_resolve")
def incident_resolve(id):
    i = Incident.query.get_or_404(id)
    i.status = "Resolved"
    db.session.commit()
    flash(f"✅ Incident #{i.id} has been resolved.", "success")
    return redirect(url_for("main.incident_detail", incident_id=i.id))

@main.route("/incident/<int:id>/edit", methods=["GET", "POST"], endpoint="incident_edit")
def incident_edit(id):
    i = Incident.query.get_or_404(id)
    form = IncidentForm()

    # Customer mapping as specified
    customer_map = {
        "customers": ["VLTX", "Bol", "Bank Muscat", "TransG"],
        "sites": {
            "VLTX": ["Birmingham","London Kings Cross","Tonbridge","Bristol","Woolston","Kilmarnock","Washington"],
            "Bol": ["Wolverhampton","Northampton","Portsmouth","Reading","Swindon","Oxford","Milton Keynes"],
            "Bank Muscat": ["Muscat","Nizwa","Sur","Sohar","Khasab","Ibra","Rustaq"],
            "TransG": ["Manchester","Liverpool","Preston","Bolton","Blackburn","Wigan","Salford"]
        },
        "locations": {
            "VLTX": ["Production Floor","Warehouse","Office Area","Loading Bay"],
            "Bol": ["Assembly Line","Quality Control","Maintenance Shop","Storage"],
            "Bank Muscat": ["Banking Hall","ATM Area","Server Room","Office"],
            "TransG": ["Dispatch Center","Vehicle Bay","Parts Store","Admin Office"]
        },
        "models": {
            "VLTX": ["7000","V-Series","X-Pro"],
            "Bol": ["7000","V-Series","Industrial-5000"],
            "Bank Muscat": ["Security-2000","7000","Compact-300"],
            "TransG": ["Heavy-Duty-8000","7000","Fleet-Manager"]
        }
    }

    FAULT_MAP = {
        "E001": "Motor overheating detected",
        "E002": "Hydraulic pressure loss",
        "E003": "Sensor calibration error",
        "E004": "Communication timeout",
        "E005": "Emergency stop activated",
        "W001": "Low fluid level warning",
        "W002": "Filter replacement due",
        "W003": "Scheduled maintenance required"
    }

    SITE_SERIAL_MAP = {
        "Birmingham": [
            ("BIRM27", "7000"),
            ("BIRM30", "7000"),
            ("BIRM35", "7000"),
            ("BIRMV01", "V-Series"),
            ("BIRMV05", "V-Series"),
        ],
        "Bristol": [
            ("BRIS28", "7000"),
            ("BRIS31", "7000"),
            ("BRISV02", "V-Series"),
        ],
        "London Kings Cross": [
            ("LKC40", "7000"),
            ("LKC45", "7000"),
            ("LKCX01", "X-Pro"),
        ],
        "Wolverhampton": [
            ("WOLV12", "7000"),
            ("WOLV15", "Industrial-5000"),
            ("WOLV18", "V-Series"),
        ],
        "Northampton": [
            ("NORT22", "7000"),
            ("NORT25", "Industrial-5000"),
        ],
        "Muscat": [
            ("MUS001", "Security-2000"),
            ("MUS002", "7000"),
            ("MUS003", "Compact-300"),
        ],
        "Manchester": [
            ("MAN100", "Heavy-Duty-8000"),
            ("MAN101", "7000"),
            ("MAN102", "Fleet-Manager"),
        ]
    }

    # Populate form choices
    form.customer_name.choices = [('', 'Select customer...')] + [(c, c) for c in customer_map["customers"]]
    form.site_name.choices = [('', 'Select site...')]
    form.location.choices = [('', 'Select location...')]
    form.machine_model.choices = [('', 'Select model...')]
    form.machine_serial.choices = [('', 'Select serial...')]
    form.fault_code.choices = [('', 'Select fault code...')] + [(code, code) for code in FAULT_MAP.keys()]
    form.fault.choices = [('', 'Select fault description...')]

    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        form.title.data = i.title
        form.description.data = i.description
        form.customer_name.data = i.customer_name
        form.site_name.data = i.site_name
        form.location.data = i.location
        form.machine_model.data = i.machine_model
        form.machine_serial.data = i.machine_serial
        form.fault_code.data = i.fault_code
        form.fault.data = i.fault
        form.start_time.data = i.start_time
        form.end_time.data = i.end_time
        form.preventive_maintenance.data = i.preventive_maintenance
        form.category.data = i.category
        form.severity.data = i.severity
        form.status.data = i.status

        # Populate dependent choices based on selected customer
        if i.customer_name:
            form.site_name.choices = [('', 'Select site...')] + [(s, s) for s in customer_map["sites"].get(i.customer_name, [])]
            form.location.choices = [('', 'Select location...')] + [(l, l) for l in customer_map["locations"].get(i.customer_name, [])]
            form.machine_model.choices = [('', 'Select model...')] + [(m, m) for m in customer_map["models"].get(i.customer_name, [])]

        # Populate serial choices based on selected site
        if i.site_name:
            pairs = SITE_SERIAL_MAP.get(i.site_name, [])
            serials = [s for (s, _m) in pairs]
            form.machine_serial.choices = [('', 'Select serial...')] + [(s, s) for s in serials]

        # Populate fault description based on selected fault code
        if i.fault_code and i.fault_code in FAULT_MAP:
            form.fault.choices = [('', 'Select fault description...'), (FAULT_MAP[i.fault_code], FAULT_MAP[i.fault_code])]

    if form.validate_on_submit():
        # Validation logic (reused from new incident route)
        customer = form.customer_name.data
        site = form.site_name.data
        location = form.location.data
        model = form.machine_model.data
        serial = form.machine_serial.data
        fault_code = form.fault_code.data
        fault_desc = form.fault.data

        # Server-side validation
        if customer and customer not in customer_map["customers"]:
            form.customer_name.errors.append("Invalid customer selection.")
        if customer and site and site not in customer_map["sites"].get(customer, []):
            form.site_name.errors.append("Invalid site for selected customer.")
        if customer and location and location not in customer_map["locations"].get(customer, []):
            form.location.errors.append("Invalid location for selected customer.")
        if customer and model and model not in customer_map["models"].get(customer, []):
            form.machine_model.errors.append("Invalid model for selected customer.")
        if site:
            valid_serials = {s for (s, _m) in SITE_SERIAL_MAP.get(site, [])}
            if serial and serial not in valid_serials:
                form.machine_serial.errors.append("Invalid serial for selected site.")
        if fault_code and fault_code not in FAULT_MAP:
            form.fault_code.errors.append("Invalid fault code.")
        if fault_code and fault_desc and fault_desc != FAULT_MAP.get(fault_code, ""):
            form.fault.errors.append("Fault description doesn't match selected code.")

        # Check if there are validation errors
        if not any([form.customer_name.errors, form.site_name.errors, form.location.errors, 
                   form.machine_model.errors, form.machine_serial.errors, form.fault_code.errors, form.fault.errors]):
            
            # Update incident with form data
            i.title = form.title.data
            i.description = form.description.data
            i.customer_name = form.customer_name.data
            i.site_name = form.site_name.data
            i.location = form.location.data
            i.machine_model = form.machine_model.data
            i.machine_serial = form.machine_serial.data
            i.fault_code = form.fault_code.data
            i.fault = form.fault.data
            i.start_time = form.start_time.data
            i.end_time = form.end_time.data
            i.preventive_maintenance = form.preventive_maintenance.data
            i.category = form.category.data
            i.severity = form.severity.data
            i.status = form.status.data

            db.session.commit()
            flash(f"✅ Incident #{i.id} has been updated successfully.", "success")
            return redirect(url_for("main.incident_detail", incident_id=i.id))

    return render_template("incident_form.html", form=form, is_edit=True, incident=i,
                          customer_map=json.dumps(customer_map),
                          fault_map=json.dumps(FAULT_MAP),
                          site_serial_map=json.dumps(SITE_SERIAL_MAP))

@main.route("/incidents/export.csv", endpoint="incidents_export")
def incidents_export():
    # Get the same query parameters as the incidents route
    q = request.args.get('q', '').strip()
    customer = request.args.get('customer', '')
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query with the same filtering logic as incidents route
    query = Incident.query
    
    # Text search filter
    if q:
        query = query.filter(
            db.or_(
                Incident.title.icontains(q),
                Incident.description.icontains(q)
            )
        )
    
    # Customer filter
    if customer:
        query = query.filter(Incident.customer_name == customer)
    
    # Status filter
    if status:
        query = query.filter(Incident.status == status)
    
    # Severity filter - only filter if severity is one of the valid choices
    if severity and severity in ['Low', 'Medium', 'High']:
        query = query.filter(Incident.severity == severity)
    
    # Date range filters
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.fromisoformat(date_from.replace('T', ' '))
            query = query.filter(Incident.created_at >= date_from_obj)
        except:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.fromisoformat(date_to.replace('T', ' '))
            query = query.filter(Incident.created_at <= date_to_obj)
        except:
            pass
    
    # Get the filtered incidents
    incidents = query.order_by(Incident.created_at.desc()).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'ID', 'Title', 'Customer', 'Severity', 'Status', 'Created At', 
        'Site', 'Model', 'Serial', 'Fault Code'
    ])
    
    # Write data rows
    for incident in incidents:
        writer.writerow([
            incident.id,
            incident.title or '',
            incident.customer_name or '',
            incident.severity or '',
            incident.status or '',
            incident.created_at.strftime('%Y-%m-%d %H:%M:%S') if incident.created_at else '',
            incident.site_name or '',
            incident.machine_model or '',
            incident.machine_serial or '',
            incident.fault_code or ''
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename="incidents.csv"'
    
    return response
