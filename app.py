from flask import Flask, render_template, request

app = Flask(__name__)

# Sample Industry Opportunities (Ayush / Biotech / Pharma)
OPPORTUNITIES = [
    {
        "id": 1,
        "title": "Ayurvedic Formulation Intern",
        "company": "Himalaya Herbal Healthcare",
        "type": "Internship",
        "required_skills": ["Phytochemistry", "Quality Control", "Standardization", "Pharmacognosy"],
        "stipend": "₹15,000/mo",
        "location": "Bengaluru"
    },
    {
        "id": 2,
        "title": "Clinical Research Associate",
        "company": "Dabur Research Foundation",
        "type": "Placement",
        "required_skills": ["GCP Guidelines", "Clinical Trials", "Data Analysis", "Pharmacovigilance"],
        "stipend": "₹5.5 LPA",
        "location": "New Delhi"
    },
    {
        "id": 3,
        "title": "Faculty Industry Immersion Program",
        "company": "Patanjali Research Institute",
        "type": "Faculty R&D",
        "required_skills": ["Herbal Drug Discovery", "Spectroscopy", "Patent Drafting"],
        "stipend": "Grant-Funded",
        "location": "Haridwar"
    }
]

@app.route("/", methods=["GET", "POST"])
def index():
    user_skills = []
    matched_results = []
    
    if request.method == "POST":
        raw_skills = request.form.get("skills", "")
        role = request.form.get("role", "Student")
        
        # Clean skills input
        user_skills = [s.strip().lower() for s in raw_skills.split(",") if s.strip()]
        
        for opp in OPPORTUNITIES:
            opp_skills = [s.lower() for s in opp["required_skills"]]
            matched = set(user_skills).intersection(set(opp_skills))
            missing = set(opp_skills) - set(user_skills)
            
            match_score = int((len(matched) / len(opp_skills)) * 100) if opp_skills else 0
            
            matched_results.append({
                **opp,
                "match_score": match_score,
                "matched_skills": [s.title() for s in matched],
                "missing_skills": [s.title() for s in missing]
            })
            
        # Sort by best match
        matched_results = sorted(matched_results, key=lambda x: x["match_score"], reverse=True)

    return render_template("index.html", results=matched_results, user_skills=",".join(user_skills))

if __name__ == "__main__":
    app.run(host="10.62.218.61", port=5000, debug=True)