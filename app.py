"""
Academia-Industry Collaboration Portal (SIH Prototype)
Skill Mapping | Internships | Placements

Stack: Python 3 + Flask + Jinja2 + Vanilla CSS/JS.
All data is held in in-memory Python structures (no external database).
"""

import os
from datetime import datetime
from functools import wraps

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sih-academia-industry-portal-dev-key")

# ---------------------------------------------------------------------------
# In-memory data stores
# ---------------------------------------------------------------------------

SKILLS = [
    "Python", "Data Analysis", "Web Development", "Machine Learning",
    "Cloud & DevOps", "Communication", "Teamwork", "Problem Solving",
]

TECHNICAL_SKILLS = SKILLS[:5]
SOFT_SKILLS = SKILLS[5:]

MOCK_USERS = {
    "student": {
        "password": "student123", "role": "student", "name": "Ayush Sharma",
        "institution": "Govt. Engineering College, Bhubaneswar",
        "branch": "Computer Science", "year": "3rd Year", "cgpa": 8.4,
    },
    "priya": {
        "password": "priya123", "role": "student", "name": "Priya Nayak",
        "institution": "Govt. Engineering College, Bhubaneswar",
        "branch": "Information Technology", "year": "4th Year", "cgpa": 9.1,
    },
    "rahul": {
        "password": "rahul123", "role": "student", "name": "Rahul Verma",
        "institution": "Govt. Engineering College, Bhubaneswar",
        "branch": "Electronics", "year": "3rd Year", "cgpa": 7.2,
    },
    "faculty": {
        "password": "faculty123", "role": "academician", "name": "Dr. Meera Iyer",
        "institution": "Govt. Engineering College, Bhubaneswar",
        "department": "Computer Science", "designation": "Assistant Professor",
    },
    "industry": {
        "password": "industry123", "role": "industry", "name": "Sanjay Rao",
        "company": "TechNova Solutions", "designation": "Talent Acquisition Lead",
    },
    "institution": {
        "password": "institution123", "role": "institution", "name": "Placement Cell",
        "institution": "Govt. Engineering College, Bhubaneswar",
        "designation": "Training & Placement Office",
    },
}

# Each question maps to one skill; every option carries a 0-4 competency weight.
ASSESSMENT_QUESTIONS = [
    {
        "id": "q1", "skill": "Python", "type": "technical",
        "text": "How comfortable are you writing Python programs?",
        "options": [
            {"text": "Never used Python", "score": 0},
            {"text": "Basic syntax, loops and functions", "score": 2},
            {"text": "OOP, file handling, libraries like pandas", "score": 3},
            {"text": "Built and deployed complete Python applications", "score": 4},
        ],
    },
    {
        "id": "q2", "skill": "Python", "type": "technical",
        "text": "Which best describes your experience with Python frameworks?",
        "options": [
            {"text": "No exposure", "score": 0},
            {"text": "Followed tutorials on Flask/Django", "score": 2},
            {"text": "Built a small project with Flask/Django/FastAPI", "score": 3},
            {"text": "Built REST APIs with authentication and testing", "score": 4},
        ],
    },
    {
        "id": "q3", "skill": "Data Analysis", "type": "technical",
        "text": "How do you handle a raw dataset with missing values?",
        "options": [
            {"text": "Not sure how to start", "score": 0},
            {"text": "Open it in Excel and clean it manually", "score": 1},
            {"text": "Use pandas to clean, group and summarise", "score": 3},
            {"text": "Build reproducible pipelines with validation and visualisation", "score": 4},
        ],
    },
    {
        "id": "q4", "skill": "Data Analysis", "type": "technical",
        "text": "Your experience with SQL and databases?",
        "options": [
            {"text": "None", "score": 0},
            {"text": "Basic SELECT queries", "score": 2},
            {"text": "Joins, aggregations and subqueries", "score": 3},
            {"text": "Schema design, indexing and query optimisation", "score": 4},
        ],
    },
    {
        "id": "q5", "skill": "Web Development", "type": "technical",
        "text": "What can you build for the web today?",
        "options": [
            {"text": "Nothing yet", "score": 0},
            {"text": "Static pages with HTML and CSS", "score": 2},
            {"text": "Dynamic pages with JavaScript and an API", "score": 3},
            {"text": "Full-stack apps with auth, database and deployment", "score": 4},
        ],
    },
    {
        "id": "q6", "skill": "Machine Learning", "type": "technical",
        "text": "Your level with machine learning?",
        "options": [
            {"text": "Only heard of it", "score": 0},
            {"text": "Know the theory of common algorithms", "score": 1},
            {"text": "Trained models with scikit-learn on real datasets", "score": 3},
            {"text": "Built, evaluated and deployed ML models end to end", "score": 4},
        ],
    },
    {
        "id": "q7", "skill": "Cloud & DevOps", "type": "technical",
        "text": "Experience with Git, CI/CD or cloud platforms?",
        "options": [
            {"text": "None", "score": 0},
            {"text": "Basic Git commit and push", "score": 1},
            {"text": "Git branching plus an app deployed on a cloud host", "score": 3},
            {"text": "Docker, CI/CD pipelines and managed cloud services", "score": 4},
        ],
    },
    {
        "id": "q8", "skill": "Communication", "type": "soft",
        "text": "How do you handle presenting technical work to an audience?",
        "options": [
            {"text": "I avoid presenting", "score": 0},
            {"text": "I can present if I read from notes", "score": 2},
            {"text": "I present confidently in class or team meetings", "score": 3},
            {"text": "I regularly present to large or external audiences", "score": 4},
        ],
    },
    {
        "id": "q9", "skill": "Teamwork", "type": "soft",
        "text": "What has been your role in group projects so far?",
        "options": [
            {"text": "Mostly worked alone", "score": 0},
            {"text": "Contributed my assigned part", "score": 2},
            {"text": "Coordinated work between teammates", "score": 3},
            {"text": "Led teams, resolved conflicts and tracked delivery", "score": 4},
        ],
    },
    {
        "id": "q10", "skill": "Problem Solving", "type": "soft",
        "text": "How do you approach an unfamiliar problem?",
        "options": [
            {"text": "Wait for guidance", "score": 0},
            {"text": "Search for a ready-made solution", "score": 2},
            {"text": "Break it down and test possible approaches", "score": 3},
            {"text": "Analyse trade-offs, prototype and justify the chosen design", "score": 4},
        ],
    },
]

# Career roles used by the skill-mapping engine.
CAREER_ROLES = [
    {"title": "Backend Developer", "industry": "IT Services / Product",
     "skills": ["Python", "Web Development", "Cloud & DevOps", "Problem Solving"],
     "demand": "High"},
    {"title": "Data Analyst", "industry": "Analytics / BFSI",
     "skills": ["Data Analysis", "Python", "Communication", "Problem Solving"],
     "demand": "High"},
    {"title": "ML Engineer", "industry": "AI / Product",
     "skills": ["Machine Learning", "Python", "Data Analysis", "Cloud & DevOps"],
     "demand": "Medium"},
    {"title": "Full Stack Developer", "industry": "Startups / IT",
     "skills": ["Web Development", "Python", "Teamwork", "Problem Solving"],
     "demand": "High"},
    {"title": "Cloud / DevOps Associate", "industry": "Cloud Services",
     "skills": ["Cloud & DevOps", "Problem Solving", "Teamwork"],
     "demand": "Medium"},
    {"title": "Business Analyst", "industry": "Consulting",
     "skills": ["Communication", "Data Analysis", "Teamwork", "Problem Solving"],
     "demand": "Medium"},
]

OPPORTUNITIES = [
    {
        "id": 1, "title": "Backend Development Intern", "org": "TechNova Solutions",
        "posted_by": "industry", "audience": "student", "type": "Internship",
        "location": "Bengaluru (Hybrid)", "duration": "6 months",
        "stipend": "Rs 25,000 / month",
        "skills": ["Python", "Web Development", "Cloud & DevOps"],
        "description": "Work with the platform team on REST APIs, database design and "
                       "deployment pipelines, mentored by senior engineers.",
        "eligibility": "3rd / 4th year B.Tech, CGPA 7.0 and above", "openings": 8,
    },
    {
        "id": 2, "title": "Data Analyst Trainee", "org": "TechNova Solutions",
        "posted_by": "industry", "audience": "student", "type": "Job",
        "location": "Hyderabad", "duration": "Full time", "stipend": "Rs 6.5 LPA",
        "skills": ["Data Analysis", "Python", "Communication"],
        "description": "Entry-level analyst role covering data cleaning, dashboards and "
                       "stakeholder reporting for BFSI clients.",
        "eligibility": "Final year or graduated, any branch", "openings": 12,
    },
    {
        "id": 3, "title": "ML Research Apprenticeship", "org": "Vedanta AI Labs",
        "posted_by": "vedanta", "audience": "student", "type": "Apprenticeship",
        "location": "Remote", "duration": "4 months", "stipend": "Rs 18,000 / month",
        "skills": ["Machine Learning", "Python", "Data Analysis"],
        "description": "Assist researchers on applied ML problems in healthcare imaging. "
                       "Publication opportunity for strong performers.",
        "eligibility": "Prior ML coursework or project", "openings": 4,
    },
    {
        "id": 4, "title": "Live Project: Smart Campus Dashboard", "org": "UrbanGrid Systems",
        "posted_by": "urbangrid", "audience": "student", "type": "Live Project",
        "location": "Bhubaneswar (On campus)", "duration": "3 months",
        "stipend": "Certificate + Rs 10,000 grant",
        "skills": ["Web Development", "Teamwork", "Problem Solving"],
        "description": "Student teams build an IoT dashboard on real sensor feeds from the "
                       "company, with weekly industry mentor reviews.",
        "eligibility": "Teams of 3-4 students", "openings": 5,
    },
    {
        "id": 5, "title": "Faculty Industrial Immersion Programme", "org": "TechNova Solutions",
        "posted_by": "industry", "audience": "academician", "type": "Faculty Internship",
        "location": "Bengaluru", "duration": "6 weeks (summer)",
        "stipend": "Rs 60,000 honorarium",
        "skills": ["Cloud & DevOps", "Python", "Communication"],
        "description": "Faculty embed with product teams to observe modern engineering "
                       "practice and redesign course content accordingly.",
        "eligibility": "Full-time faculty with 2+ years experience", "openings": 10,
    },
    {
        "id": 6, "title": "FDP: Industry-Aligned Curriculum in AI", "org": "Vedanta AI Labs",
        "posted_by": "vedanta", "audience": "academician", "type": "FDP",
        "location": "Online + 2-day workshop", "duration": "2 weeks",
        "stipend": "Fully sponsored (AICTE approved)",
        "skills": ["Machine Learning", "Data Analysis", "Communication"],
        "description": "Faculty Development Programme covering AI curriculum design, lab "
                       "exercises and industry case studies.",
        "eligibility": "Faculty from AICTE-approved institutions", "openings": 40,
    },
    {
        "id": 7, "title": "Consultancy: Predictive Maintenance Study", "org": "UrbanGrid Systems",
        "posted_by": "urbangrid", "audience": "academician", "type": "Consultancy",
        "location": "Bhubaneswar", "duration": "9 months",
        "stipend": "Rs 4.5 L project grant",
        "skills": ["Machine Learning", "Data Analysis", "Problem Solving"],
        "description": "Collaborative research and consultancy on predictive maintenance for "
                       "utility infrastructure, with co-authored publications.",
        "eligibility": "Faculty with a relevant research background", "openings": 2,
    },
    {
        "id": 8, "title": "Industrial Training: Embedded Systems Lab", "org": "UrbanGrid Systems",
        "posted_by": "urbangrid", "audience": "academician", "type": "Industrial Training",
        "location": "Pune", "duration": "10 days", "stipend": "Travel + stay covered",
        "skills": ["Problem Solving", "Teamwork"],
        "description": "Hands-on training on industrial embedded toolchains so labs can be "
                       "rebuilt around current hardware practice.",
        "eligibility": "Faculty teaching electronics or embedded courses", "openings": 20,
    },
]

LEARNING_PROGRAMS = [
    {
        "id": 101, "title": "Python for Industry Readiness", "provider": "TechNova Solutions",
        "type": "Certification Course", "mode": "Online, self-paced", "duration": "6 weeks",
        "skills": ["Python", "Problem Solving"],
        "description": "Industry-authored Python track ending in a proctored certification "
                       "recognised by hiring partners.",
    },
    {
        "id": 102, "title": "Applied Data Analytics Bootcamp", "provider": "Vedanta AI Labs",
        "type": "Bootcamp", "mode": "Weekend live sessions", "duration": "8 weeks",
        "skills": ["Data Analysis", "Communication"],
        "description": "SQL, pandas and dashboarding on real anonymised industry datasets, "
                       "with a capstone reviewed by practising analysts.",
    },
    {
        "id": 103, "title": "Cloud Foundations & DevOps Workshop", "provider": "UrbanGrid Systems",
        "type": "Workshop", "mode": "Hybrid", "duration": "3 days",
        "skills": ["Cloud & DevOps"],
        "description": "Git workflows, containers and CI/CD pipelines with hands-on labs on a "
                       "sponsored cloud sandbox.",
    },
    {
        "id": 104, "title": "Technical Communication & Interview Craft",
        "provider": "TechNova Solutions", "type": "Mentorship Programme",
        "mode": "Online, 1:1 mentors", "duration": "4 weeks",
        "skills": ["Communication", "Teamwork"],
        "description": "Mock interviews, resume clinics and presentation coaching by "
                       "practising engineers and HR leads.",
    },
    {
        "id": 105, "title": "Machine Learning Practitioner Certification",
        "provider": "Vedanta AI Labs", "type": "Certification Course", "mode": "Online",
        "duration": "10 weeks", "skills": ["Machine Learning", "Python", "Data Analysis"],
        "description": "Supervised learning, model evaluation and deployment, with a graded "
                       "industry capstone project.",
    },
    {
        "id": 106, "title": "Full Stack Web Engineering Track", "provider": "TechNova Solutions",
        "type": "Certification Course", "mode": "Online + weekly mentor call",
        "duration": "12 weeks", "skills": ["Web Development", "Python", "Cloud & DevOps"],
        "description": "Build and deploy three production-style web applications reviewed by "
                       "the company's engineering team.",
    },
]

COLLABORATIONS = [
    {"title": "Guest Lecture Series: Engineering at Scale", "org": "TechNova Solutions",
     "type": "Guest Lecture", "slots": "4 sessions per semester",
     "description": "Industry architects deliver lectures mapped to the Software Engineering "
                    "syllabus."},
    {"title": "Innovation Challenge: Sustainable Cities", "org": "UrbanGrid Systems",
     "type": "Innovation Challenge", "slots": "Team entries open",
     "description": "Joint student-faculty teams solve live civic problems; winning ideas are "
                    "funded for a pilot."},
    {"title": "Collaborative Research: Federated Learning for Health", "org": "Vedanta AI Labs",
     "type": "Research Project", "slots": "2 faculty partners",
     "description": "Two-year joint research with shared IP, industry compute credits and "
                    "student research assistants."},
    {"title": "Industry Mentorship Pool", "org": "TechNova Solutions",
     "type": "Mentorship", "slots": "25 mentors available",
     "description": "Engineers mentor final-year projects and review student portfolios each "
                    "month."},
    {"title": "Workshop: Secure Coding Practices", "org": "TechNova Solutions",
     "type": "Workshop", "slots": "60 seats",
     "description": "Two-day hands-on workshop for students and faculty on secure development "
                    "and code review."},
]

# Applications lodged against opportunities.
APPLICATIONS = [
    {"id": 1, "username": "priya", "opportunity_id": 2, "status": "Shortlisted",
     "applied_on": "2026-08-12", "match": 82,
     "timeline": ["Applied on 2026-08-12", "Under Review on 2026-08-16",
                  "Shortlisted on 2026-08-24"]},
    {"id": 2, "username": "priya", "opportunity_id": 1, "status": "Under Review",
     "applied_on": "2026-08-19", "match": 74,
     "timeline": ["Applied on 2026-08-19", "Under Review on 2026-08-25"]},
    {"id": 3, "username": "rahul", "opportunity_id": 4, "status": "Applied",
     "applied_on": "2026-08-28", "match": 58,
     "timeline": ["Applied on 2026-08-28"]},
]

STUDENT_PORTFOLIO = {
    "student": {
        "skills": {},
        "assessment_done": False,
        "certifications": [
            {"name": "Python for Industry Readiness", "issuer": "TechNova Solutions",
             "year": "2026", "verified": True},
        ],
        "projects": [
            {"name": "Campus Grievance Portal", "tech": "Flask, SQLite",
             "detail": "Web portal used by 400+ students to track hostel complaints.",
             "verified": True},
            {"name": "Air Quality Visualiser", "tech": "Python, pandas",
             "detail": "Dashboard of city AQI trends built from open government data.",
             "verified": False},
        ],
        "internships": [
            {"role": "Web Development Intern", "org": "Nexa Softwares",
             "duration": "May - Jul 2026",
             "feedback": "Delivered assigned modules on time; strong learning attitude.",
             "verified": True},
        ],
        "achievements": [
            {"name": "Runner-up, State Level Hackathon", "year": "2026", "verified": True},
        ],
    },
    "priya": {
        "skills": {"Python": 88, "Data Analysis": 92, "Web Development": 70,
                   "Machine Learning": 65, "Cloud & DevOps": 55,
                   "Communication": 85, "Teamwork": 80, "Problem Solving": 82},
        "assessment_done": True, "assessed_on": "2026-08-05",
        "certifications": [{"name": "Applied Data Analytics Bootcamp",
                            "issuer": "Vedanta AI Labs", "year": "2026", "verified": True}],
        "projects": [{"name": "Retail Sales Forecasting", "tech": "Python, scikit-learn",
                      "detail": "Forecast model with 12% error reduction over the baseline.",
                      "verified": True}],
        "internships": [{"role": "Analytics Intern", "org": "TechNova Solutions",
                         "duration": "Jun - Aug 2026",
                         "feedback": "Excellent SQL and stakeholder communication.",
                         "verified": True}],
        "achievements": [{"name": "Best Paper, Student Symposium", "year": "2026",
                          "verified": True}],
    },
    "rahul": {
        "skills": {"Python": 45, "Data Analysis": 38, "Web Development": 52,
                   "Machine Learning": 25, "Cloud & DevOps": 30,
                   "Communication": 60, "Teamwork": 72, "Problem Solving": 55},
        "assessment_done": True, "assessed_on": "2026-08-18",
        "certifications": [],
        "projects": [{"name": "IoT Smart Meter", "tech": "Arduino, C",
                      "detail": "Prototype energy meter with a mobile readout.",
                      "verified": True}],
        "internships": [],
        "achievements": [{"name": "Robotics Club Lead", "year": "2026", "verified": False}],
    },
}

STATUS_FLOW = ["Applied", "Under Review", "Shortlisted", "Selected", "Rejected"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def current_user():
    username = session.get("username")
    if not username or username not in MOCK_USERS:
        return None
    user = dict(MOCK_USERS[username])
    user.pop("password", None)
    user["username"] = username
    return user


def login_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                flash("Please sign in to continue.", "error")
                return redirect(url_for("login", next=request.path))
            if roles and user["role"] not in roles:
                flash("That section is not available for your role.", "error")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)
        return wrapper
    return decorator


def portfolio_for(username):
    return STUDENT_PORTFOLIO.setdefault(username, {
        "skills": {}, "assessment_done": False, "certifications": [],
        "projects": [], "internships": [], "achievements": [],
    })


def match_score(skills, required):
    """Percentage compatibility between a skill profile and required skills."""
    if not required:
        return 0
    return round(sum(skills.get(s, 0) for s in required) / len(required))


def opportunity_by_id(oid):
    return next((o for o in OPPORTUNITIES if o["id"] == oid), None)


def applications_for(username):
    return [a for a in APPLICATIONS if a["username"] == username]


def has_applied(username, oid):
    return any(a["username"] == username and a["opportunity_id"] == oid for a in APPLICATIONS)


def strengths_and_gaps(skills):
    strengths = sorted([s for s, v in skills.items() if v >= 70],
                       key=lambda s: skills[s], reverse=True)
    gaps = sorted([s for s, v in skills.items() if v < 50], key=lambda s: skills[s])
    return strengths, gaps


def recommended_roles(skills, limit=None):
    scored = [dict(r, match=match_score(skills, r["skills"])) for r in CAREER_ROLES]
    scored.sort(key=lambda r: r["match"], reverse=True)
    return scored[:limit] if limit else scored


def recommended_opportunities(user, limit=None):
    skills = portfolio_for(user["username"])["skills"] if user["role"] == "student" else {}
    audience = "academician" if user["role"] == "academician" else "student"
    items = [dict(o, match=match_score(skills, o["skills"]))
             for o in OPPORTUNITIES if o["audience"] == audience]
    items.sort(key=lambda o: o["match"], reverse=True)
    return items[:limit] if limit else items


def recommended_programs(skills, limit=None):
    """Rank programmes by how much of the student's skill gap they close."""
    items = []
    for p in LEARNING_PROGRAMS:
        closes = [s for s in p["skills"] if skills.get(s, 0) < 60]
        items.append(dict(p, closes=closes,
                          priority=sum(60 - skills.get(s, 0) for s in closes)))
    items.sort(key=lambda p: p["priority"], reverse=True)
    return items[:limit] if limit else items


def placement_readiness(skills):
    if not skills:
        return 0
    return round(sum(skills.values()) / len(skills))


def all_students():
    return [u for u in MOCK_USERS if MOCK_USERS[u]["role"] == "student"]


@app.context_processor
def inject_globals():
    return {"user": current_user(), "year": datetime.now().year}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


@app.route("/")
def home():
    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = MOCK_USERS.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["role"] = user["role"]
            flash("Welcome back, %s." % user["name"], "success")
            return redirect(request.form.get("next") or url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html", next=request.args.get("next", ""))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Role-based dashboard
# ---------------------------------------------------------------------------


@app.route("/dashboard")
@login_required()
def dashboard():
    user = current_user()
    data = {}

    if user["role"] == "student":
        pf = portfolio_for(user["username"])
        skills = pf["skills"]
        strengths, gaps = strengths_and_gaps(skills)
        data.update({
            "portfolio": pf, "skills": skills, "strengths": strengths, "gaps": gaps,
            "readiness": placement_readiness(skills),
            "roles": recommended_roles(skills, 3),
            "matches": recommended_opportunities(user, 3),
            "programs": recommended_programs(skills, 2),
            "applications": applications_for(user["username"]),
        })

    elif user["role"] == "academician":
        data.update({
            "matches": recommended_opportunities(user, 3),
            "collaborations": COLLABORATIONS[:3],
            "applications": applications_for(user["username"]),
        })

    elif user["role"] == "industry":
        company = MOCK_USERS[user["username"]]["company"]
        postings = [o for o in OPPORTUNITIES if o["posted_by"] == user["username"]]
        posting_ids = {o["id"] for o in postings}
        applicants = [a for a in APPLICATIONS if a["opportunity_id"] in posting_ids]
        data.update({
            "company": company, "postings": postings, "applicants": applicants,
            "shortlisted": [a for a in applicants
                            if a["status"] in ("Shortlisted", "Selected")],
            "programs": [p for p in LEARNING_PROGRAMS if p["provider"] == company],
        })

    else:  # institution
        data.update(institution_analytics())

    return render_template("index.html", **data)


# ---------------------------------------------------------------------------
# Skill assessment and skill mapping
# ---------------------------------------------------------------------------


@app.route("/assessment", methods=["GET", "POST"])
@login_required("student")
def assessment():
    user = current_user()
    pf = portfolio_for(user["username"])

    if request.method == "POST":
        totals, counts, unanswered = {}, {}, 0
        for q in ASSESSMENT_QUESTIONS:
            answer = request.form.get(q["id"])
            if answer is None:
                unanswered += 1
                continue
            score = q["options"][int(answer)]["score"]
            totals[q["skill"]] = totals.get(q["skill"], 0) + score
            counts[q["skill"]] = counts.get(q["skill"], 0) + 1

        if unanswered:
            flash("Please answer all %d questions - %d still unanswered."
                  % (len(ASSESSMENT_QUESTIONS), unanswered), "error")
            return render_template("assessment.html", questions=ASSESSMENT_QUESTIONS)

        pf["skills"] = {s: round(totals[s] / counts[s] / 4 * 100) for s in totals}
        pf["assessment_done"] = True
        pf["assessed_on"] = datetime.now().strftime("%Y-%m-%d")
        flash("Assessment submitted. Your skill profile has been generated.", "success")
        return redirect(url_for("skill_map"))

    return render_template("assessment.html", questions=ASSESSMENT_QUESTIONS)


@app.route("/skill-map")
@login_required("student")
def skill_map():
    user = current_user()
    pf = portfolio_for(user["username"])
    skills = pf["skills"]
    strengths, gaps = strengths_and_gaps(skills)
    return render_template(
        "skill_map.html", portfolio=pf, skills=skills, strengths=strengths, gaps=gaps,
        technical=TECHNICAL_SKILLS, soft=SOFT_SKILLS,
        readiness=placement_readiness(skills),
        roles=recommended_roles(skills),
        matches=recommended_opportunities(user, 4),
        programs=recommended_programs(skills, 3),
    )


# ---------------------------------------------------------------------------
# Opportunities: search, apply, track
# ---------------------------------------------------------------------------


@app.route("/opportunities")
@login_required()
def opportunities():
    user = current_user()
    query = request.args.get("q", "").strip().lower()
    otype = request.args.get("type", "")

    all_items = recommended_opportunities(user)
    items = all_items
    if query:
        items = [o for o in items
                 if query in o["title"].lower() or query in o["org"].lower()
                 or any(query in s.lower() for s in o["skills"])]
    if otype:
        items = [o for o in items if o["type"] == otype]

    applied_ids = [a["opportunity_id"] for a in applications_for(user["username"])]
    return render_template("opportunities.html", items=items, query=query, otype=otype,
                           types=sorted({o["type"] for o in all_items}),
                           applied_ids=applied_ids)


@app.route("/opportunity/<int:oid>")
@login_required()
def opportunity_detail(oid):
    user = current_user()
    opp = opportunity_by_id(oid)
    if not opp:
        flash("Opportunity not found.", "error")
        return redirect(url_for("opportunities"))
    skills = portfolio_for(user["username"])["skills"] if user["role"] == "student" else {}
    missing = [s for s in opp["skills"] if skills.get(s, 0) < 60]
    return render_template("opportunity_detail.html", opp=opp, skills=skills, missing=missing,
                           match=match_score(skills, opp["skills"]),
                           applied=has_applied(user["username"], oid),
                           programs=[p for p in LEARNING_PROGRAMS
                                     if set(p["skills"]) & set(missing)])


@app.route("/apply/<int:oid>", methods=["POST"])
@login_required("student", "academician")
def apply(oid):
    user = current_user()
    opp = opportunity_by_id(oid)
    if not opp:
        flash("Opportunity not found.", "error")
        return redirect(url_for("opportunities"))
    if has_applied(user["username"], oid):
        flash("You have already applied to this opportunity.", "error")
        return redirect(url_for("opportunity_detail", oid=oid))

    skills = portfolio_for(user["username"])["skills"] if user["role"] == "student" else {}
    today = datetime.now().strftime("%Y-%m-%d")
    APPLICATIONS.append({
        "id": max([a["id"] for a in APPLICATIONS], default=0) + 1,
        "username": user["username"], "opportunity_id": oid, "status": "Applied",
        "applied_on": today, "match": match_score(skills, opp["skills"]),
        "timeline": ["Applied on %s" % today],
    })
    flash("Application submitted for %s." % opp["title"], "success")
    return redirect(url_for("applications"))


@app.route("/applications")
@login_required("student", "academician")
def applications():
    user = current_user()
    items = []
    for a in applications_for(user["username"]):
        opp = opportunity_by_id(a["opportunity_id"])
        if opp:
            items.append({"app": a, "opp": opp})
    items.sort(key=lambda i: i["app"]["applied_on"], reverse=True)
    return render_template("applications.html", items=items, flow=STATUS_FLOW)


# ---------------------------------------------------------------------------
# Learning programmes, collaboration, digital portfolio
# ---------------------------------------------------------------------------


@app.route("/learning")
@login_required()
def learning():
    user = current_user()
    skills = portfolio_for(user["username"])["skills"] if user["role"] == "student" else {}
    return render_template("learning.html", programs=recommended_programs(skills), skills=skills)


@app.route("/collaboration")
@login_required()
def collaboration():
    return render_template("collaboration.html", collaborations=COLLABORATIONS)


@app.route("/portfolio")
@login_required("student")
def portfolio():
    user = current_user()
    pf = portfolio_for(user["username"])
    sections = ("certifications", "projects", "internships", "achievements")
    verified = sum(1 for k in sections for item in pf[k] if item.get("verified"))
    total = sum(len(pf[k]) for k in sections)
    return render_template("portfolio.html", portfolio=pf, skills=pf["skills"],
                           verified=verified, total=total,
                           readiness=placement_readiness(pf["skills"]))


@app.route("/portfolio/add", methods=["POST"])
@login_required("student")
def portfolio_add():
    user = current_user()
    pf = portfolio_for(user["username"])
    section = request.form.get("section")
    title = request.form.get("title", "").strip()
    detail = request.form.get("detail", "").strip()

    if not title:
        flash("A title is required.", "error")
    elif section == "certifications":
        pf["certifications"].append({"name": title, "issuer": detail or "Self-reported",
                                     "year": str(datetime.now().year), "verified": False})
        flash("Certification added. Pending verification by your institution.", "success")
    elif section == "projects":
        pf["projects"].append({"name": title, "tech": detail or "-",
                               "detail": detail or "-", "verified": False})
        flash("Project added. Pending verification by your institution.", "success")
    elif section == "achievements":
        pf["achievements"].append({"name": title, "year": str(datetime.now().year),
                                   "verified": False})
        flash("Achievement added. Pending verification by your institution.", "success")
    else:
        flash("Unknown portfolio section.", "error")
    return redirect(url_for("portfolio"))


# ---------------------------------------------------------------------------
# Industry portal
# ---------------------------------------------------------------------------


@app.route("/industry/post", methods=["GET", "POST"])
@login_required("industry")
def industry_post():
    user = current_user()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        skills = request.form.getlist("skills")
        if not title or not skills:
            flash("A title and at least one required skill are needed.", "error")
        else:
            OPPORTUNITIES.append({
                "id": max(o["id"] for o in OPPORTUNITIES) + 1,
                "title": title,
                "org": MOCK_USERS[user["username"]]["company"],
                "posted_by": user["username"],
                "audience": request.form.get("audience", "student"),
                "type": request.form.get("type", "Internship"),
                "location": request.form.get("location", "").strip() or "Not specified",
                "duration": request.form.get("duration", "").strip() or "Not specified",
                "stipend": request.form.get("stipend", "").strip() or "As per company norms",
                "skills": skills,
                "description": request.form.get("description", "").strip()
                or "No description provided.",
                "eligibility": request.form.get("eligibility", "").strip()
                or "Open to all eligible candidates",
                "openings": int(request.form.get("openings") or 1),
            })
            flash("Opportunity published. Matched candidates can see it immediately.",
                  "success")
            return redirect(url_for("industry_applicants"))
    return render_template("industry_post.html", all_skills=SKILLS)


@app.route("/industry/applicants")
@login_required("industry")
def industry_applicants():
    user = current_user()
    postings = [o for o in OPPORTUNITIES if o["posted_by"] == user["username"]]
    rows = []
    for opp in postings:
        for a in APPLICATIONS:
            if a["opportunity_id"] != opp["id"]:
                continue
            rows.append({"app": a, "opp": opp,
                         "candidate": MOCK_USERS.get(a["username"], {}),
                         "skills": portfolio_for(a["username"])["skills"]})
    rows.sort(key=lambda r: r["app"]["match"], reverse=True)
    return render_template("industry_applicants.html", rows=rows, postings=postings,
                           flow=STATUS_FLOW)


@app.route("/industry/status/<int:aid>", methods=["POST"])
@login_required("industry")
def industry_status(aid):
    status = request.form.get("status")
    row = next((a for a in APPLICATIONS if a["id"] == aid), None)
    if not row or status not in STATUS_FLOW:
        flash("Could not update that application.", "error")
    else:
        row["status"] = status
        row["timeline"].append("%s on %s" % (status, datetime.now().strftime("%Y-%m-%d")))
        flash("Application marked as %s." % status, "success")
    return redirect(url_for("industry_applicants"))


# ---------------------------------------------------------------------------
# Institution analytics
# ---------------------------------------------------------------------------


def institution_analytics():
    students = all_students()
    profiles = {u: portfolio_for(u)["skills"] for u in students}
    assessed = [u for u in students if portfolio_for(u)["assessment_done"]]

    avg_skills = {}
    for skill in SKILLS:
        scored = [profiles[u].get(skill, 0) for u in assessed]
        avg_skills[skill] = round(sum(scored) / len(scored)) if scored else 0

    demand = {}
    for o in OPPORTUNITIES:
        for s in o["skills"]:
            demand[s] = demand.get(s, 0) + 1
    demand_ranked = sorted(demand.items(), key=lambda kv: kv[1], reverse=True)

    rows = []
    for u in students:
        apps = applications_for(u)
        rows.append({
            "username": u, "profile": MOCK_USERS[u],
            "readiness": placement_readiness(profiles[u]),
            "assessed": portfolio_for(u)["assessment_done"],
            "applications": len(apps),
            "placed": any(a["status"] == "Selected" for a in apps),
            "shortlisted": any(a["status"] == "Shortlisted" for a in apps),
        })
    rows.sort(key=lambda r: r["readiness"], reverse=True)

    return {
        "students": rows,
        "total_students": len(students),
        "assessed_count": len(assessed),
        "avg_skills": avg_skills,
        "demand": demand_ranked,
        "gap_skills": sorted(avg_skills.items(), key=lambda kv: kv[1])[:3],
        "total_applications": len(APPLICATIONS),
        "placed_count": sum(1 for r in rows if r["placed"]),
        "shortlisted_count": sum(1 for r in rows if r["shortlisted"]),
        "ready_count": sum(1 for r in rows if r["readiness"] >= 70),
        "avg_readiness": round(sum(r["readiness"] for r in rows) / len(rows)) if rows else 0,
        "opportunity_count": len(OPPORTUNITIES),
        "program_count": len(LEARNING_PROGRAMS),
    }


@app.route("/analytics")
@login_required("institution")
def analytics():
    return render_template("analytics.html", **institution_analytics())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
