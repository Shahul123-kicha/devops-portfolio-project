from datetime import datetime
import os
from flask import Flask, redirect, render_template_string, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite Database locally inside the container/app folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tirupati_autos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Database Model for Auto Drivers
class AutoDriver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(100), nullable=False)
    auto_number = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    stand_location = db.Column(db.String(100), nullable=False)  # e.g., Alipiri, Railway Station, Tirumala
    status = db.Column(db.String(20), default="Available")  # Available / On Trip
    registered_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )


# HTML Frontend Template with Dashboard & Registration Form
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tirupati Auto Drivers Real-Time Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; margin: 0; padding: 20px; color: #334155; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { color: #0284c7; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #64748b; margin-bottom: 30px; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 30px; }
        input, select { padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
        button { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 16px; cursor: pointer; grid-column: span full; }
        button:hover { background: #0369a1; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #f8fafc; color: #475569; font-weight: 600; }
        .badge-available { background: #dcfce7; color: #166534; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .badge-ontrip { background: #fee2e2; color: #991b1b; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛺 Tirupati Auto Fleet & Real-Time Hub</h1>
        <div class="subtitle">Live Dispatch and Driver Tracking System</div>

        <!-- Form to Register New Auto Driver -->
        <form action="/add" method="POST" class="form-grid">
            <input type="text" name="driver_name" placeholder="Driver Full Name" required>
            <input type="text" name="auto_number" placeholder="Auto Number (e.g., AP03X1234)" required>
            <input type="text" name="phone_number" placeholder="Phone Number" required>
            <select name="stand_location" required>
                <option value="" disabled selected>Select Stand Location</option>
                <option value="Alipiri Toll Gate">Alipiri Toll Gate</option>
                <option value="Tirupati Railway Station">Tirupati Railway Station</option>
                <option value="Tirumula Bus Stand">Tirumula Bus Stand</option>
                <option value="RTC Bus Stand">RTC Bus Stand</option>
                <option value="Kapila Theertham">Kapila Theertham</option>
            </select>
            <select name="status">
                <option value="Available">Available</option>
                <option value="On Trip">On Trip</option>
            </select>
            <button type="submit">Register / Update Driver</button>
        </form>

        <h2>Active Registered Drivers in Tirupati</h2>
        <table>
            <thead>
                <tr>
                    <th>Driver Name</th>
                    <th>Auto Number</th>
                    <th>Phone</th>
                    <th>Stand Location</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for driver in drivers %}
                <tr>
                    <td>{{ driver.driver_name }}</td>
                    <td><strong>{{ driver.auto_number }}</strong></td>
                    <td>{{ driver.phone_number }}</td>
                    <td>{{ driver.stand_location }}</td>
                    <td>
                        {% if driver.status == 'Available' %}
                            <span class="badge-available">Available</span>
                        {% else %}
                            <span class="badge-ontrip">On Trip</span>
                        {% endif %}
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="5" style="text-align: center; color: #94a3b8;">No drivers registered yet. Add one above!</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    all_drivers = AutoDriver.query.order_by(AutoDriver.id.desc()).all()
    return render_template_string(HTML_PAGE, drivers=all_drivers)


@app.route("/add", methods=["POST"])
def add_driver():
    name = request.form.get("driver_name")
    auto_num = request.form.get("auto_number")
    phone = request.form.get("phone_number")
    stand = request.form.get("stand_location")
    status = request.form.get("status")

    # Check if auto number already exists, update or add new
    existing = AutoDriver.query.filter_by(auto_number=auto_num).first()
    if existing:
        existing.driver_name = name
        existing.phone_number = phone
        existing.stand_location = stand
        existing.status = status
    else:
        new_driver = AutoDriver(
            driver_name=name,
            auto_number=auto_num,
            phone_number=phone,
            stand_location=stand,
            status=status,
        )
        db.session.add(new_driver)

    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Automatically creates SQLite database file
    app.run(host="0.0.0.0", port=5000)