import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("mock_resumes.json")
LABEL_OUTPUT = Path(__file__).with_name("mock_labels.json")

PROFILES = [
    {
        "band": "strong",
        "skills": "JavaScript, React, Node.js, Express.js, SQL, PostgreSQL, Git, Docker, AWS",
        "bullets": [
            "Built REST APIs with Node.js and Express.js for a student placement platform",
            "Developed responsive React dashboards backed by PostgreSQL",
            "Containerized services with Docker and deployed them to AWS",
        ],
        "education": "B.Tech Computer Science, 2026",
    },
    {
        "band": "strong",
        "skills": "JavaScript, React.js, Node, REST APIs, MySQL, Git, Docker",
        "bullets": [
            "Implemented React components and Node REST services for a campus marketplace",
            "Designed SQL queries and data models in MySQL",
            "Used Git pull requests and Docker Compose in a four-person team",
        ],
        "education": "B.E. Information Technology, 2026",
    },
    {
        "band": "partial",
        "skills": "JavaScript, React, TypeScript, Node.js, MongoDB, Git",
        "bullets": [
            "Created accessible React interfaces for an event discovery application",
            "Built Node.js endpoints and stored document data in MongoDB",
            "Reviewed changes through Git branches and pull requests",
        ],
        "education": "B.Tech Computer Science, 2026",
    },
    {
        "band": "partial",
        "skills": "JavaScript, Vue.js, Express, SQL, Git, REST",
        "bullets": [
            "Built responsive Vue views for an inventory tracker",
            "Maintained Express REST routes and SQL reports",
            "Collaborated with designers and engineers using Git",
        ],
        "education": "B.Sc. Software Engineering, 2025",
    },
    {
        "band": "partial",
        "skills": "Python, Django, JavaScript, React, SQLite, Git",
        "bullets": [
            "Developed Django services and small React admin screens",
            "Modeled application data with SQLite and wrote integration tests",
            "Tracked work in Git and documented API behavior",
        ],
        "education": "B.Tech Computer Science, 2027",
    },
    {
        "band": "adjacent",
        "skills": "Python, FastAPI, PostgreSQL, Docker, Git, REST APIs",
        "bullets": [
            "Implemented FastAPI services for a research data portal",
            "Optimized PostgreSQL queries and automated local environments with Docker",
            "Worked in an agile team with Git code review",
        ],
        "education": "M.C.A., 2026",
    },
    {
        "band": "adjacent",
        "skills": "Java, Spring Boot, JavaScript, MySQL, Git, REST APIs",
        "bullets": [
            "Developed Spring Boot REST endpoints for a library system",
            "Built simple JavaScript pages and MySQL reports",
            "Used Git workflows and wrote unit tests for service logic",
        ],
        "education": "B.Tech Information Technology, 2026",
    },
    {
        "band": "weak",
        "skills": "C++, Java, Data Structures, Algorithms, Git",
        "bullets": [
            "Solved algorithmic programming problems and contributed to a C++ project",
            "Practiced object-oriented design and basic testing",
            "Used Git for coursework submissions",
        ],
        "education": "B.Tech Computer Science, 2027",
    },
    {
        "band": "weak",
        "skills": "Figma, HTML, CSS, UX Research, Canva",
        "bullets": [
            "Designed mobile-first prototypes for a student wellness application",
            "Ran usability interviews and synthesized user feedback",
            "Presented interaction flows to a cross-functional project team",
        ],
        "education": "B.Des. Interaction Design, 2026",
    },
    {
        "band": "weak",
        "skills": "Excel, Power BI, SQL, Data Analysis, Python",
        "bullets": [
            "Cleaned survey data and built Power BI dashboards",
            "Wrote SQL queries for weekly reporting",
            "Automated spreadsheet checks with Python scripts",
        ],
        "education": "B.Sc. Data Science, 2026",
    },
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Arjun", "Diya", "Ishaan", "Kavya", "Meera", "Nikhil",
    "Rhea", "Saanvi", "Vihaan", "Zoya", "Ananya", "Dev", "Ira", "Kabir",
    "Maya", "Neel", "Pari", "Rohan", "Tara", "Yash", "Anika", "Karan",
]
LAST_NAMES = [
    "Sharma", "Patel", "Rao", "Nair", "Kapoor", "Mehta", "Iyer", "Joshi",
    "Bose", "Das", "Gupta", "Menon", "Singh", "Verma", "Kulkarni",
]


def build_dataset():
    resumes = []
    labels = []
    for index in range(120):
        profile = PROFILES[index % len(PROFILES)]
        first = FIRST_NAMES[index % len(FIRST_NAMES)]
        last = LAST_NAMES[(index * 3) % len(LAST_NAMES)]
        candidate_id = f"r{index + 1:03d}"
        name = f"{first} {last}"
        bullets = [f"{bullet} (cohort project {index // len(PROFILES) + 1})" for bullet in profile["bullets"]]
        raw_text = (
            f"{name}\n\nSummary\nComputer science student seeking a software internship.\n\n"
            f"Skills\n{profile['skills']}\n\nExperience\n- "
            + "\n- ".join(bullets)
            + f"\n\nEducation\n{profile['education']}"
        )
        resumes.append(
            {
                "id": candidate_id,
                "name": name,
                "raw_text": raw_text,
                "skills_section": profile["skills"].lower(),
                "experience_bullets": bullets,
                "education": profile["education"],
            }
        )
        labels.append({"resume_id": candidate_id, "expected_fit": profile["band"]})
    return resumes, labels


if __name__ == "__main__":
    resumes, labels = build_dataset()
    OUTPUT.write_text(json.dumps({"resumes": resumes}, indent=2) + "\n", encoding="utf-8")
    LABEL_OUTPUT.write_text(json.dumps({"labels": labels}, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(resumes)} resumes and {len(labels)} evaluation labels")