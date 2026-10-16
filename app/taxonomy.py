"""Taxonomy and keyword dictionaries for resume and job description analysis.

Contains categorized technical & soft skills, action verbs, clichés,
and standard resume section patterns.
"""

# Categorized Skill Taxonomy
SKILLS_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "golang", "go",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "shell",
        "bash", "powershell", "perl", "haskell", "lua", "elixir", "clojure", "sql", "html", "css"
    ],
    "Web & Frameworks": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "svelte", "node.js",
        "express", "express.js", "fastapi", "flask", "django", "spring", "spring boot",
        "asp.net", ".net core", "ruby on rails", "laravel", "graphql", "rest api", "restful api",
        "tailwind", "tailwindcss", "bootstrap", "sass", "redux", "zustand", "prisma",
        "grpc", "websockets", "microservices"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "google cloud", "gcp", "docker",
        "kubernetes", "k8s", "terraform", "ansible", "jenkins", "gitlab ci", "github actions",
        "circleci", "helm", "linux", "nginx", "apache", "prometheus", "grafana",
        "datadog", "cloudformation", "ec2", "s3", "lambda", "ecs", "eks", "serverless",
        "ci/cd", "devops", "site reliability", "sre"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "dynamodb", "cassandra", "sqlite", "oracle", "mariadb", "neo4j", "supabase",
        "firebase", "snowflake", "bigquery", "redshift", "kafka", "rabbitmq"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "artificial intelligence", "nlp",
        "natural language processing", "computer vision", "pytorch", "tensorflow", "keras",
        "scikit-learn", "pandas", "numpy", "scipy", "llm", "large language models",
        "langchain", "rag", "hugging face", "transformers", "openai", "data analysis",
        "data engineering", "spark", "hadoop", "tableau", "power bi"
    ],
    "Tools & Methodologies": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "agile", "scrum", "kanban", "ci/cd", "tdd", "test driven development",
        "unit testing", "integration testing", "jest", "pytest", "cypress", "selenium",
        "postman", "swagger", "system design", "software architecture", "oop", "clean code"
    ],
    "Soft Skills & Leadership": [
        "leadership", "team leadership", "mentorship", "cross-functional collaboration",
        "communication", "problem solving", "critical thinking", "project management",
        "stakeholder management", "time management", "adaptability", "teamwork",
        "conflict resolution", "decision making", "presentation skills", "code review"
    ]
}

# Strong Action Verbs for ATS & impact measurement
POWER_ACTION_VERBS = [
    "accelerated", "accomplished", "achieved", "acquired", "administered", "advanced",
    "analyzed", "architected", "automated", "boosted", "built", "centralized", "championed",
    "coached", "collaborated", "compiled", "composed", "conceptualized", "constructed",
    "created", "cultivated", "debugged", "decreased", "delivered", "deployed", "designed",
    "developed", "devised", "diagnosed", "directed", "discovered", "documented", "doubled",
    "drove", "eliminated", "enabled", "engineered", "enhanced", "established", "evaluated",
    "executed", "expanded", "expedited", "fabricated", "facilitated", "fine-tuned", "forecasted",
    "formulated", "founded", "generated", "guided", "halted", "headed", "identified",
    "implemented", "improved", "increased", "initiated", "innovated", "inspected", "installed",
    "instituted", "instructed", "integrated", "intensified", "invented", "investigated",
    "launched", "led", "leveraged", "managed", "maximized", "mentored", "migrated",
    "minimized", "modernized", "monitored", "negotiated", "operated", "optimized", "orchestrated",
    "organized", "outperformed", "overhauled", "oversaw", "partnered", "pioneered", "planned",
    "prevented", "programmed", "published", "re-engineered", "rebuilt", "reconciled", "recruited",
    "redesigned", "reduced", "refactored", "refined", "remodeled", "reorganized", "replaced",
    "resolved", "restructured", "revamped", "reviewed", "revitalized", "saved", "scaled",
    "secured", "simplified", "solved", "spearheaded", "standardized", "streamlined", "strengthened",
    "supervised", "surpassed", "trained", "transformed", "unified", "upgraded", "validated",
    "yielded"
]

# Weak / Passive Verbs to flag for improvement
WEAK_WORDS = [
    "assisted with", "helped with", "worked on", "handled", "responsible for", "duties included",
    "participated in", "did", "made", "attempted", "contributed to", "involved in", "tried",
    "tasked with", "served as", "part of a team that", "supported"
]

# Clichés and Empty Buzzwords
CLICHE_BUZZWORDS = [
    "hard worker", "go-getter", "team player", "out-of-the-box thinker", "detail-oriented",
    "results-driven", "self-motivated", "dynamic professional", "synergy", "think outside the box",
    "fast-paced environment", "people person", "guru", "rockstar", "ninja", "wear many hats",
    "hit the ground running", "strategic thinker", "passionate worker"
]

# Standard Resume Section Headers for ATS Section Matching
STANDARD_SECTIONS = {
    "contact": ["contact", "personal info", "contact information"],
    "summary": ["summary", "professional summary", "profile", "about me", "executive summary", "objective"],
    "experience": ["experience", "work experience", "employment history", "professional experience", "work history"],
    "education": ["education", "academic history", "qualifications", "educational background"],
    "skills": ["skills", "technical skills", "technologies", "core competencies", "competencies", "areas of expertise"],
    "projects": ["projects", "personal projects", "key projects", "notable projects", "technical projects"],
    "certifications": ["certifications", "licenses", "certificates", "credentials", "professional certifications"],
    "awards": ["awards", "honors", "achievements", "accomplishments", "publications"]
}
