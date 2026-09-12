"""Conservative canonical skill and alias normalization."""

from __future__ import annotations

import re


ALIASES = {
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "react native": "React Native",
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "vue": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "redux": "Redux",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "express.js": "Express.js",
    "express": "Express.js",
    "nestjs": "NestJS",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring": "Spring Boot",
    "rest apis": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "rest": "REST API",
    "graphql": "GraphQL",
    "python": "Python",
    "java": "Java",
    "kotlin": "Kotlin",
    "dart": "Dart",
    "flutter": "Flutter",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "ruby": "Ruby",
    "sql": "SQL",
    "sqlite": "SQLite",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "firebase": "Firebase",
    "android sdk": "Android SDK",
    "android": "Android",
    "ios": "iOS",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "microservices": "Microservices",
    "agile": "Agile",
    "scrum": "Scrum",
}


def normalize_skill(value: str) -> str | None:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    return ALIASES.get(normalized)


def extract_skill_mentions(text: str) -> list[str]:
    normalized = text.lower()
    matches: list[str] = []
    occupied: list[tuple[int, int]] = []

    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        for match in re.finditer(rf"(?<!\w){re.escape(alias)}(?!\w)", normalized):
            span = match.span()
            if any(span[0] < end and start < span[1] for start, end in occupied):
                continue
            occupied.append(span)
            if canonical not in matches:
                matches.append(canonical)

    return matches
