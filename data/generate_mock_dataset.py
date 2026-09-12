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


def infer_canonical_skill(text: str) -> str:
    normalized = text.lower().strip()
    aliases = {
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "node": "Node.js",
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "express": "Express.js",
        "express.js": "Express.js",
        "sql": "SQL",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "docker": "Docker",
        "aws": "AWS",
        "mongodb": "MongoDB",
        "git": "Git",
        "typescript": "TypeScript",
        "javascript": "JavaScript",
        "python": "Python",
        "fastapi": "FastAPI",
        "django": "Django",
        "java": "Java",
        "spring boot": "Spring Boot",
        "rest api": "REST API",
        "rest apis": "REST API",
        "vue.js": "Vue.js",
        "sqlite": "SQLite",
        "power bi": "Power BI",
        "figma": "Figma",
        "html": "HTML",
        "css": "CSS",
        "ux research": "UX Research",
        "canva": "Canva",
        "c++": "C++",
        "data structures": "Data Structures",
        "algorithms": "Algorithms",
        "excel": "Excel",
        "rest": "REST API",
    }
    return aliases.get(normalized, text.strip())


def build_evidence(candidate_id: str, profile: dict, cohort_index: int):
    evidence = [
        {
            "candidate_id": candidate_id,
            "evidence_id": f"{candidate_id}_skill_01",
            "section": "skills",
            "text": profile["skills"],
            "page": 1,
            "position": 1,
            "extracted_skill": "JavaScript",
            "canonical_skill": "JavaScript",
            "evidence_type": "skill_list",
            "source": "skills",
            "evidence_source_type": "skills_section",
            "evidence_strength": "applied",
        }
    ]

    for idx, bullet in enumerate(profile["bullets"], start=1):
        lower = bullet.lower()
        extracted = "JavaScript"
        for candidate_skill in [
            "node.js",
            "react",
            "express",
            "sql",
            "postgresql",
            "mysql",
            "docker",
            "aws",
            "mongodb",
            "python",
            "fastapi",
            "django",
            "java",
            "spring boot",
            "vue.js",
            "power bi",
            "figma",
            "html",
            "css",
            "ux research",
            "rest api",
            "rest apis",
        ]:
            if candidate_skill in lower:
                extracted = infer_canonical_skill(candidate_skill)
                break

        evidence.append(
            {
                "candidate_id": candidate_id,
                "evidence_id": f"{candidate_id}_exp_{idx:02d}",
                "section": "experience",
                "text": f"{bullet} (cohort project {cohort_index})",
                "page": 1,
                "position": idx + 1,
                "extracted_skill": extracted,
                "canonical_skill": extracted,
                "evidence_type": "project_or_experience",
                "source": "experience",
                "evidence_source_type": "project",
                "evidence_strength": "substantial",
            }
        )

    return evidence


def build_dataset():
    candidates = []
    labels = []

    for index in range(120):
        profile = PROFILES[index % len(PROFILES)]
        first = FIRST_NAMES[index % len(FIRST_NAMES)]
        last = LAST_NAMES[(index * 3) % len(LAST_NAMES)]
        candidate_id = f"candidate_{index + 1:03d}"
        name = f"{first} {last}"
        cohort_index = index // len(PROFILES) + 1
        bullets = [f"{bullet} (cohort project {cohort_index})" for bullet in profile["bullets"]]
        raw_text = (
            f"{name}\n\nSummary\nComputer science student seeking a software internship.\n\n"
            f"Skills\n{profile['skills']}\n\nExperience\n- "
            + "\n- ".join(bullets)
            + f"\n\nEducation\n{profile['education']}"
        )

        candidate = {
            "candidate_id": candidate_id,
            "candidate_name": name,
            "resume_source": f"synthetic_resume_{index + 1:03d}.txt",
            "raw_text": raw_text,
            "sections": {
                "summary": "Computer science student seeking a software internship.",
                "skills": profile["skills"],
                "experience": bullets,
                "education": profile["education"],
            },
            "evidence": build_evidence(candidate_id, profile, cohort_index),
            "metadata": {
                "band": profile["band"],
                "synthetic": True,
            },
        }
        candidates.append(candidate)
        labels.append({"candidate_id": candidate_id, "expected_fit": profile["band"]})

    return {
        "job_description": {
            "title": "Junior Full Stack Developer Intern",
            "company": "TechNova Solutions",
            "source": "synthetic_job_description.pdf",
        },
        "candidates": candidates,
    }, {"labels": labels}


if __name__ == "__main__":
    dataset, labels = build_dataset()
    OUTPUT.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")
    LABEL_OUTPUT.write_text(json.dumps(labels, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(dataset['candidates'])} candidates and {len(labels['labels'])} evaluation labels")
