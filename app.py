from flask import Flask, jsonify,request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="cseaiml2025",
        database="od"
    )

@app.route("/api/donors", methods=["GET", "POST"])
def donors():

    if request.method == "GET":
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM donors")
            data = cursor.fetchall()

            cursor.close()
            conn.close()

            return jsonify(data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    elif request.method == "POST":
        try:
            data = request.get_json()

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
    INSERT INTO donors
    (
        full_name,
        age,
        blood_group,
        organ,
        medical_status,
        donation_type,
        phone,
        donation_status
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
""", (
    data.get("full_name"),
    data.get("age"),
    data.get("blood_group"),
    data.get("organ"),
    data.get("medical_status"),
    data.get("donation_type"),
    data.get("phone"),
    "Not Donated"
))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Donor Registered Successfully"}), 201

        except Exception as e:
            print("DONOR ERROR:", e)
            return jsonify({"error": str(e)}), 500
        
# ---------------- EMERGENCY REQUESTS ----------------
@app.route("/api/emergency", methods=["GET"])
def get_emergency_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
    SELECT 
        request_id,
        patient_name,
        age,
        blood_group,
        required_organ,
        urgency_level,
        hospital_id,
        doctor_name,
        contact_number,
        LOWER(status) AS status
    FROM emergency_requests
""")
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/emergency/<int:request_id>/resolve", methods=["PUT"])
def resolve_emergency(request_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE emergency_requests
            SET status = 'resolved'
            WHERE request_id = %s
        """, (request_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Marked as resolved"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/analytics/summary")
def analytics_summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM donors")
    donors = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM recipients")
    recipients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM donor_recipient_match WHERE match_status='Successful'")
    matches = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return jsonify({
        "donors": donors,
        "recipients": recipients,
        "matches": matches
    })

@app.route("/api/analytics/donors_by_organ")
def donors_by_organ():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT organ AS organ, COUNT(*) AS count
        FROM donors
        GROUP BY organ
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(data)

@app.route("/api/analytics/recipients_by_blood")
def recipients_by_blood():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT blood_group AS blood_group, COUNT(*) AS count
        FROM recipients
        GROUP BY blood_group
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(data)

@app.route("/api/analytics/monthly_matches")
def monthly_matches():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            match_id AS month,
            COUNT(*) AS count
        FROM donor_recipient_match
        GROUP BY match_id
        ORDER BY match_id
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)

@app.route("/api/recipients", methods=["GET", "POST"])
def recipients():

    # ---------------- GET RECIPIENTS ----------------
    if request.method == "GET":

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM recipients")
            recipients = cursor.fetchall()

            cursor.close()
            conn.close()

            return jsonify(recipients)

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500

    # ---------------- ADD RECIPIENT ----------------
    elif request.method == "POST":

        try:
            data = request.get_json()

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO recipients
(
    full_name,
    age,
    blood_group,
    required_organ,
    urgency_level,
    medical_condition,
    phone,
    organ_received
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                (
    data["full_name"],
    data["age"],
    data["blood_group"],
    data["required_organ"],
    data["urgency_level"],
    data["medical_condition"],
    data["phone"],
    "Not Received"
)
            ))

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message":
                "Recipient Registered Successfully"
            })

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500
# ---------------- UPDATE DONOR STATUS ----------------
@app.route("/api/donor/<int:donor_id>/donated",
methods=["PUT"])
def mark_donor_donated(donor_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE donors
            SET donation_status='Donated'
            WHERE donor_id=%s
        """, (donor_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message":
            "Donor marked as donated"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
    # ---------------- UPDATE RECIPIENT STATUS ----------------
@app.route("/api/recipient/<int:recipient_id>/received",
methods=["PUT"])
def mark_recipient_received(recipient_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE recipients
            SET organ_received='Received'
            WHERE recipient_id=%s
        """, (recipient_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message":
            "Recipient marked as received"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
    # ---------------- USER LOGIN ----------------
@app.route("/api/user-login", methods=["POST"])
def user_login():

    try:
        data = request.get_json()

        username = data["username"]
        password = data["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users
            (
                username,
                password
            )
            VALUES (%s,%s)
        """, (
            username,
            password
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message":
            "User Login Saved"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hospitals")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)


# UPDATE HOSPITAL (ADMIN ONLY)
@app.route("/api/hospitals/<int:hospital_id>", methods=["PUT"])
def update_hospital(hospital_id):

    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE hospitals
            SET icu_beds = %s,
                doctors = %s
            WHERE hospital_id = %s
        """, (
            data.get("icu_beds"),
            data.get("doctors"),
            hospital_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Hospital updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/hospitals", methods=["POST"])
def add_hospital():
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO hospitals 
            (hospital_name, location, icu_beds, doctors, specialization, contact_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["hospital_name"],
            data["location"],
            data["icu_beds"],
            data["doctors"],
            data["specialization"],
            data["contact_number"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Hospital added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ---------------- ORGAN AVAILABILITY ----------------
@app.route("/api/organs", methods=["GET"])
def get_organs():

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Get organ + hospital name (FIXED JOIN)
        cursor.execute("""
            SELECT
                o.organ_id AS id,
                o.organ_name,
                o.blood_group,
                o.available_donors,
                o.status,
                o.hospital_id,
                h.hospital_name
            FROM organ_availability o
            JOIN hospitals h
            ON o.hospital_id = h.hospital_id
        """)

        organs = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(organs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- UPDATE ORGAN DONORS (+ / -) ----------------
@app.route("/api/organs/<int:id>", methods=["PUT"])
def update_organ(id):

    try:
        data = request.get_json()
        new_donors = data.get("available_donors")

        conn = get_db_connection()   # ✅ SAME DB USED
        cursor = conn.cursor()

        # ✅ UPDATE correct table
        cursor.execute("""
            UPDATE organ_availability
            SET available_donors = %s
            WHERE organ_id = %s
        """, (new_donors, id))

        conn.commit()

        # (optional) auto status update
        if new_donors == 0:
            cursor.execute("""
                UPDATE organ_availability
                SET status = 'Limited'
                WHERE organ_id = %s
            """, (id,))
            conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Organ updated successfully",
            "id": id,
            "available_donors": new_donors
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "LifeLink API Running"

if __name__ == "__main__":
    app.run(debug=True)