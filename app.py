from flask import Flask, render_template, request
import os
import PyPDF2

app = Flask(__name__)

# -------------------------------
# UPLOAD FOLDER
# -------------------------------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------------
# SKILLS DATABASE
# -------------------------------
skills_list = [
    "python","java","c++","machine learning","deep learning",
    "sql","mysql","html","css","javascript","react","node.js",
    "flask","django","pandas","numpy","power bi"
]

# -------------------------------
# DOMAIN SKILLS
# -------------------------------
domain_skills = {
    "data science": ["python","pandas","numpy","machine learning","statistics","sql","data visualization"],
    "web development": ["html","css","javascript","react","node.js","mongodb"],
    "ai ml": ["python","machine learning","deep learning","nlp","tensorflow"]
}

# -------------------------------
# COURSES DATABASE
# -------------------------------
courses_db = {
    "python": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
    "html": "https://www.youtube.com/watch?v=qz0aGYrrlhU",
    "css": "https://www.youtube.com/watch?v=1Rs2ND1ryYc",
    "javascript": "https://www.youtube.com/watch?v=W6NZfCO5SIk",

    "machine learning": "https://www.youtube.com/watch?v=GwIo3gDZCVQ",
    "deep learning": "https://www.youtube.com/watch?v=aircAruvnKk",

    "sql": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
    "pandas": "https://www.youtube.com/watch?v=vmEHCJofslg",
    "numpy": "https://www.youtube.com/watch?v=QUT1VHiLmmI",

    "statistics": "https://www.youtube.com/watch?v=xxpc-HPKN28",
    "data visualization": "https://www.youtube.com/watch?v=GpQoP0x9thk",

    "react": "https://www.youtube.com/watch?v=bMknfKXIFA8",
    "node.js": "https://www.youtube.com/watch?v=TlB_eWDSMt4",
    "mongodb": "https://www.youtube.com/watch?v=ofme2o29ngU"
}

# -------------------------------
# JOB DATABASE
# -------------------------------
job_db = [
    {"title": "Junior Data Scientist","domain":"data science",
     "skills_required":["python","numpy","pandas","machine learning"]},
    {"title": "Frontend Developer","domain":"web development",
     "skills_required":["html","css","javascript","react"]},
    {"title": "AI/ML Intern","domain":"ai ml",
     "skills_required":["python","machine learning","deep learning"]}
]

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("home.html")

# ✅ Manual Page (FIXED)
@app.route("/manual")
def manual():
    return render_template("manual.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/job_match_page")
def job_match_page():
    return render_template("job_match.html")

# -------------------------------
# 🔹 MANUAL ANALYZER (NO JOBS)
# -------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    domain = request.form["domain"]
    user_skills = [s.strip().lower() for s in request.form["skills"].split(",")]

    missing_skills = find_skill_gap(user_skills, domain)
    courses = recommend_courses(missing_skills)
    roadmap = generate_roadmap(domain, missing_skills)

    return render_template("result.html",
                           skills=user_skills,
                           missing_skills=missing_skills,
                           courses=courses,
                           roadmap=roadmap,
                           show_jobs=False)  # ❌ No jobs here

# -------------------------------
# 🔹 RESUME ANALYZER (WITH JOBS)
# -------------------------------
@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    file = request.files["resume"]
    domain = request.form["domain"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    text = extract_text(filepath)
    user_skills = extract_skills(text)

    missing_skills = find_skill_gap(user_skills, domain)
    courses = recommend_courses(missing_skills)
    roadmap = generate_roadmap(domain, missing_skills)

    jobs = recommend_jobs(user_skills)

    return render_template("result.html",
                           skills=user_skills,
                           missing_skills=missing_skills,
                           courses=courses,
                           roadmap=roadmap,
                           jobs=jobs,
                           show_jobs=True)  # ✅ Jobs shown

# -------------------------------
# 🔹 JOB MATCHER
# -------------------------------
@app.route("/job_match", methods=["POST"])
def job_match():
    file = request.files["resume"]
    job_desc = request.form["job_desc"].lower()

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    resume_text = extract_text(filepath)
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc)

    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]

    match_percent = int((len(matched)/len(job_skills))*100) if job_skills else 0
    courses = recommend_courses(missing)

    jobs = recommend_jobs(resume_skills)

    return render_template("job_result.html",
                           match_percent=match_percent,
                           matched=matched,
                           missing=missing,
                           courses=courses,
                           jobs=jobs)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def extract_text(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()

def extract_skills(text):
    return [skill for skill in skills_list if skill in text]

def find_skill_gap(user_skills, domain):
    return [s for s in domain_skills.get(domain, []) if s not in user_skills]

def recommend_courses(missing_skills):
    courses = {}
    for skill in missing_skills:
        courses[skill] = f"https://www.youtube.com/results?search_query={skill}"
    return courses

def generate_roadmap(domain, missing):
    return [f"Learn {s}" for s in missing]

def recommend_jobs(user_skills):
    result = []
    for job in job_db:
        matched = [s for s in job["skills_required"] if s in user_skills]
        percent = int((len(matched)/len(job["skills_required"]))*100)
        if percent > 0:
            result.append({
                "title": job["title"],
                "domain": job["domain"],
                "match_percent": percent,
                "matched_skills": matched,
                "missing_skills": [s for s in job["skills_required"] if s not in user_skills]
            })
    return sorted(result, key=lambda x: x["match_percent"], reverse=True)

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)