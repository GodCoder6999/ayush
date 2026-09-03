import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "ayush_portal_super_secret_key"

# Simulated User Accounts for Each Role
MOCK_USERS = {
    "student@ayush.in": {"password": "123", "role": "student", "name": "Arjun Sharma"},
    "faculty@aiia.in": {"password": "123", "role": "faculty", "name": "Dr. Ramesh Varma"},
    "recruiter@dabur.com": {"password": "123", "role": "industry", "name": "Dabur HR Team"},
    "admin@aiia.in": {"password": "123", "role": "institution", "name": "Dean Academic Affairs"}
}

ASSESSMENT_QUESTIONS = [
    {
        "id": "q1",
        "category": "Technical",
        "question": "Experience with Phytochemical Screening & Extraction:",
        "skill": "Phytochemistry",
        "options": [
            {"label": "No prior experience", "weight": 0},
            {"label": "Basic lab classroom knowledge", "weight": 40},
            {"label": "Conducted independent HPLC/HPTLC profiling", "weight": 100}
        ]
    },
    {
        "id": "q2",
        "category": "Technical",
        "question": "Familiarity with Herbal Drug Standardization & GMP:",
        "skill": "Quality Control & GMP",
        "options": [
            {"label": "Beginner / Unfamiliar", "weight": 0},
            {"label": "Understand API/Ayush Pharmacopoeia specs", "weight": 60},
            {"label": "Implemented Batch Validation & Quality Testing", "weight": 100}
        ]
    },
    {
        "id": "q3",
        "category": "Technical",
        "question": "Clinical Trials & GCP Protocol:",
        "skill": "Clinical Research & GCP",
        "options": [
            {"label": "Never exposed", "weight": 0},
            {"label": "Certified in Basic GCP Guidelines", "weight": 60},
            {"label": "Managed clinical data & trial reporting", "weight": 100}
        ]
    },
    {
        "id": "q4",
        "category": "Soft Skills",
        "question": "Cross-Functional Collaboration & Reporting:",
        "skill": "Documentation & Collaboration",
        "options": [
            {"label": "Need guidance", "weight": 30},
            {"label": "Comfortable drafting SOPs & presenting to teams", "weight": 100}
        ]
    }
]

OPPORTUNITIES = [
    {
        "id": 1,
        "title": "Ayurvedic Formulation Intern",
        "company": "Himalaya Herbal Healthcare",
        "category": "Internship",
        "audience": "student",
        "required_skills": ["Phytochemistry", "Quality Control & GMP"],
        "stipend": "₹18,000/mo",
        "location": "Bengaluru"
    },
    {
        "id": 2,
        "title": "Clinical Research Associate",
        "company": "Dabur Research Foundation",
        "category": "Placement",
        "audience": "student",
        "required_skills": ["Clinical Research & GCP", "Documentation & Collaboration"],
        "stipend": "₹6.2 LPA",
        "location": "New Delhi"
    },
    {
        "id": 3,
        "title": "Faculty Industrial Immersion & FDP",
        "company": "Patanjali Research Institute",
        "category": "Faculty FDP",
        "audience": "faculty",
        "required_skills": ["Phytochemistry", "Quality Control & GMP"],
        "stipend": "₹50,000 Research Grant",
        "location": "Haridwar"
    },
    {
        "id": 4,
        "title": "Consultancy: Ayush Formulation Scale-up",
        "company": "Baidyanath R&D",
        "category": "Consultancy",
        "audience": "faculty",
        "required_skills": ["Quality Control & GMP"],
        "stipend": "Retainer Basis",
        "location": "Kolkata"
    }
]

LEARNING_PROGRAMS = [
    {"name": "Herbal Extraction Masterclass", "provider": "All India Institute of Ayurveda", "skill": "Phytochemistry", "duration": "4 Weeks"},
    {"name": "Ayush Clinical Trial Management (CTM)", "provider": "Ministry of Ayush e-Learning", "skill": "Clinical Research & GCP", "duration": "6 Weeks"},
    {"name": "Standardization of ASU Drugs & GMP", "provider": "Pharmacopoeia Commission", "skill": "Quality Control & GMP", "duration": "3 Weeks"}
]

APPLICATIONS = []
STUDENT_PORTFOLIO = {
    "name": "Arjun Sharma",
    "institution": "All India Institute of Ayurveda (AIIA)",
    "verified_skills": ["Phytochemistry"],
    "certifications": ["Ayush Good Laboratory Practices (GLP) 2025"]
}

# --- AUTHENTICATION ROUTES ---

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = MOCK_USERS.get(email)
        if user and user["password"] == password:
            session["user"] = {
                "email": email,
                "role": user["role"],
                "name": user["name"]
            }
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Email or Password. Please select one of the pre-filled demo roles below."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- DASHBOARD ROUTE ---

@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    current_user = session["user"]
    tab = current_user["role"]

    return render_template(
        "index.html",
        user=current_user,
        tab=tab,
        questions=ASSESSMENT_QUESTIONS,
        opportunities=OPPORTUNITIES,
        courses=LEARNING_PROGRAMS,
        portfolio=STUDENT_PORTFOLIO,
        applications=APPLICATIONS,
        total_applied=len(APPLICATIONS),
        total_openings=len(OPPORTUNITIES)
    )

@app.route("/assess", methods=["POST"])
def assess_skills():
    if "user" not in session:
        return redirect(url_for("login"))

    verified = []
    gaps = []
    for q in ASSESSMENT_QUESTIONS:
        score = int(request.form.get(q["id"], 0))
        if score >= 60:
            verified.append(q["skill"])
        else:
            gaps.append(q["skill"])

    STUDENT_PORTFOLIO["verified_skills"] = verified

    matched_opportunities = []
    for opp in OPPORTUNITIES:
        req = set(opp["required_skills"])
        acquired = req.intersection(set(verified))
        missing = req - acquired
        score = int((len(acquired) / len(req)) * 100) if req else 100
        
        matched_opportunities.append({
            **opp,
            "match_score": score,
            "matched_skills": list(acquired),
            "missing_skills": list(missing)
        })

    matched_opportunities = sorted(matched_opportunities, key=lambda x: x["match_score"], reverse=True)

    return render_template(
        "index.html",
        user=session["user"],
        tab="student",
        assessment_done=True,
        verified_skills=verified,
        skill_gaps=gaps,
        matched_opportunities=matched_opportunities,
        questions=ASSESSMENT_QUESTIONS,
        courses=LEARNING_PROGRAMS,
        portfolio=STUDENT_PORTFOLIO,
        applications=APPLICATIONS,
        total_applied=len(APPLICATIONS),
        total_openings=len(OPPORTUNITIES)
    )

@app.route("/apply", methods=["POST"])
def apply_opportunity():
    if "user" not in session:
        return redirect(url_for("login"))

    opp_id = int(request.form.get("opp_id"))
    opp = next((o for o in OPPORTUNITIES if o["id"] == opp_id), None)
    if opp and not any(a["id"] == opp_id for a in APPLICATIONS):
        APPLICATIONS.append({
            "id": opp["id"],
            "title": opp["title"],
            "company": opp["company"],
            "category": opp["category"],
            "status": "Shortlisted for Review"
        })
    return redirect(url_for("dashboard"))

@app.route("/post-job", methods=["POST"])
def post_job():
    if "user" not in session:
        return redirect(url_for("login"))

    new_id = len(OPPORTUNITIES) + 1
    OPPORTUNITIES.append({
        "id": new_id,
        "title": request.form.get("title"),
        "company": request.form.get("company"),
        "category": request.form.get("category"),
        "audience": request.form.get("audience"),
        "required_skills": [s.strip() for s in request.form.get("skills").split(",") if s.strip()],
        "stipend": request.form.get("stipend"),
        "location": request.form.get("location")
    })
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)