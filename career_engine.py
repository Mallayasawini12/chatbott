import re
import json
import os
import requests
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


# Rich structured data for the 5 career paths
CAREER_DATA = {
    "software_developer": {
        "title": "Software Developer / Engineer",
        "description": "Software Developers design, build, and maintain software systems and applications. They solve complex problems, write clean code, and collaborate with teams to build digital products.",
        "roadmap": [
            {"phase": "Phase 1: Foundations", "details": "Learn programming fundamentals (Python, Java, or C++), Version Control (Git/GitHub), and basic terminal usage."},
            {"phase": "Phase 2: Core Concepts", "details": "Master Data Structures & Algorithms (Arrays, Lists, Trees, Graphs, Sorting, Searching) and Object-Oriented Programming (OOP) principles."},
            {"phase": "Phase 3: Database & Tools", "details": "Learn SQL (PostgreSQL, MySQL) and NoSQL (MongoDB) databases. Understand RESTful APIs and basic software architectures (MVC)."},
            {"phase": "Phase 4: Advanced & Deployment", "details": "Study System Design, Testing (Unit, Integration), CI/CD pipelines, Docker containerization, and Cloud fundamentals (AWS or GCP)."},
            {"phase": "Phase 5: Placement Ready", "details": "Build 2-3 substantial projects, practice coding on LeetCode/HackerRank, and study behavioral & system design questions."}
        ],
        "skills": {
            "programming": ["Python", "Java", "C++", "Go", "C#"],
            "databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB"],
            "tools": ["Git", "GitHub", "Docker", "Linux", "Kubernetes", "VS Code"],
            "concepts": ["Data Structures", "Algorithms", "OOP", "System Design", "CI/CD", "Testing"]
        },
        "courses": [
            {"name": "CS50: Introduction to Computer Science", "platform": "Harvard / edX", "link": "https://www.edx.org/course/introduction-computer-science-harvardx-cs50x"},
            {"name": "Data Structures and Algorithms Specialization", "platform": "UC San Diego / Coursera", "link": "https://www.coursera.org/specializations/data-structures-algorithms"},
            {"name": "Complete Git Guide", "platform": "Udemy", "link": "https://www.udemy.com/"}
        ],
        "certifications": [
            "AWS Certified Developer - Associate",
            "Oracle Certified Professional: Java SE Developer",
            "Scrum Alliance Certified ScrumMaster (CSM)"
        ],
        "placement_tips": [
            "Build a strong GitHub profile showing commit history and collaboration.",
            "Solve at least 150-200 LeetCode problems, focusing on medium-difficulty arrays, trees, and dynamic programming.",
            "Prepare for behavior questions using the STAR method (Situation, Task, Action, Result).",
            "Practice mock system design interviews."
        ],
        "higher_studies": "Consider a Master of Science (MS) or Master of Technology (M.Tech) in Computer Science, focusing on Software Engineering, Distributed Systems, or Cloud Computing.",
        "internships": "Look for Software Engineering Intern roles on LinkedIn, Handshake, or Internshala. Focus on contributing to open source (e.g., GSoC) or building full-stack products."
    },
    "data_scientist": {
        "title": "Data Scientist",
        "description": "Data Scientists analyze complex datasets to uncover actionable insights, build predictive models, and guide strategic business decisions using mathematics, statistics, and programming.",
        "roadmap": [
            {"phase": "Phase 1: Math & Programming", "details": "Learn Python (or R), Linear Algebra, Calculus, and Probability & Statistics."},
            {"phase": "Phase 2: Data Handling", "details": "Master SQL, and learn Python libraries like NumPy, Pandas, and Matplotlib/Seaborn for data manipulation and visualization."},
            {"phase": "Phase 3: Machine Learning", "details": "Study Supervised (Linear Regression, Decision Trees) and Unsupervised (K-means, PCA) Machine Learning using Scikit-Learn."},
            {"phase": "Phase 4: Advanced Analytics & Big Data", "details": "Learn Deep Learning fundamentals, Natural Language Processing (NLP), and Big Data tools like Apache Spark & Hadoop."},
            {"phase": "Phase 5: Storytelling & Deployment", "details": "Master BI tools (Tableau, PowerBI), learn to deploy models using Flask/FastAPI, and build a portfolio of data analysis projects."}
        ],
        "skills": {
            "programming": ["Python", "R", "SQL"],
            "databases": ["PostgreSQL", "BigQuery", "Snowflake"],
            "tools": ["Jupyter", "Tableau", "PowerBI", "Git", "Spark"],
            "concepts": ["Statistics", "Linear Algebra", "Machine Learning", "Data Visualization", "Data Wrangling", "Feature Engineering"]
        },
        "courses": [
            {"name": "Google Data Analytics Professional Certificate", "platform": "Google / Coursera", "link": "https://www.coursera.org/professional-certificates/google-data-analytics"},
            {"name": "Machine Learning Specialization", "platform": "DeepLearning.AI / Stanford / Coursera", "link": "https://www.coursera.org/specializations/machine-learning-introduction"},
            {"name": "Applied Data Science with Python Specialization", "platform": "University of Michigan / Coursera", "link": "https://www.coursera.org/specializations/data-science-python"}
        ],
        "certifications": [
            "Google Cloud Certified Professional Data Engineer",
            "Microsoft Certified: Power BI Data Analyst Associate",
            "IBM Data Science Professional Certificate"
        ],
        "placement_tips": [
            "Publish your datasets and analysis notebooks on Kaggle.",
            "Write blog posts (Medium/Dev.to) explaining your analysis projects in non-technical terms.",
            "Be prepared to solve SQL query challenges during coding rounds (joins, window functions, CTEs).",
            "Ensure you can explain the mathematical intuition behind ML models you list in your resume."
        ],
        "higher_studies": "Pursue an MS in Data Science, Business Analytics, or Statistics. Ph.D. is highly valued for research-intensive data science positions.",
        "internships": "Apply for Data Analyst, Business Intelligence, or Junior Data Scientist internships. Focus on internships that give exposure to real-world messy data."
    },
    "cybersecurity_analyst": {
        "title": "Cybersecurity Analyst",
        "description": "Cybersecurity Analysts protect an organization's network, servers, and data from malicious attacks, breaches, and unauthorized access. They monitor activity, investigate alerts, and build defense systems.",
        "roadmap": [
            {"phase": "Phase 1: IT Fundamentals", "details": "Master Computer Networking (TCP/IP, DNS, Routing), Operating Systems (Linux, Windows Server), and Command Line interfaces."},
            {"phase": "Phase 2: Security Principles", "details": "Understand core security concepts: Threat modeling, cryptography, access controls, firewalls, and VPNs."},
            {"phase": "Phase 3: Defensive & Offensive Tools", "details": "Learn packet analysis with Wireshark, vulnerability scanning with Nessus, and basic scripting (Python/Bash) for security automation."},
            {"phase": "Phase 4: SIEM & Incident Response", "details": "Gain hands-on experience with Security Information and Event Management (SIEM) tools like Splunk and learn incident response steps."},
            {"phase": "Phase 5: Certification & Labs", "details": "Practice on TryHackMe/HackTheBox, study for CompTIA Security+, and build a security lab portfolio."}
        ],
        "skills": {
            "programming": ["Python", "Bash", "PowerShell"],
            "databases": ["SQL", "NoSQL"],
            "tools": ["Wireshark", "Splunk", "Nmap", "Metasploit", "Linux", "Burp Suite"],
            "concepts": ["Networking", "Cryptography", "Penetration Testing", "Vulnerability Assessment", "Firewalls", "Incident Response"]
        },
        "courses": [
            {"name": "Google Cybersecurity Professional Certificate", "platform": "Google / Coursera", "link": "https://www.coursera.org/professional-certificates/google-cybersecurity"},
            {"name": "CompTIA Security+ Exam Prep", "platform": "Various / Professor Messer", "link": "https://www.professormesser.com/"},
            {"name": "Practical Ethical Hacking", "platform": "TCM Security", "link": "https://tcm-sec.com/"}
        ],
        "certifications": [
            "CompTIA Security+",
            "Certified Information Systems Security Professional (CISSP)",
            "Offensive Security Certified Professional (OSCP)",
            "CEH (Certified Ethical Hacker)"
        ],
        "placement_tips": [
            "Build a home lab representing a small enterprise network and document how you secure it on your blog.",
            "Participate in Capture The Flag (CTF) security competitions and write detailed walk-throughs.",
            "Focus on networking protocols: be prepared to explain exactly what happens during a TCP 3-way handshake or a DNS query.",
            "Join local security meetups (OWASP, DefCon Groups) to network."
        ],
        "higher_studies": "Pursue an MS in Cybersecurity, Information Assurance, or Computer Science with a security track.",
        "internships": "Look for Security Operations Center (SOC) Analyst Intern, IT Security Intern, or System Administrator Intern roles."
    },
    "ai_ml_engineer": {
        "title": "AI / ML Engineer",
        "description": "AI/ML Engineers research, build, and deploy machine learning models and artificial intelligence applications. They work with deep learning, natural language processing, computer vision, and neural network architectures.",
        "roadmap": [
            {"phase": "Phase 1: Advanced Math & Programming", "details": "Learn Python, Advanced Probability, Statistics, Linear Algebra, Multivariate Calculus, and optimization theory."},
            {"phase": "Phase 2: Core Machine Learning", "details": "Master classical ML algorithms (regression, classification, clustering, ensemble methods) and model evaluation using Scikit-Learn."},
            {"phase": "Phase 3: Deep Learning & Frameworks", "details": "Understand Artificial Neural Networks (ANNs), CNNs for vision, RNNs/Transformers for sequence data using TensorFlow or PyTorch."},
            {"phase": "Phase 4: NLP, Vision, & LLMs", "details": "Study Natural Language Processing (NLP), Computer Vision, Generative AI, Large Language Models (LLMs), and prompt engineering."},
            {"phase": "Phase 5: MLOps & Deployment", "details": "Learn to package models into APIs, track experiments (MLflow/WandB), deploy models to cloud endpoints, and monitor data drift."}
        ],
        "skills": {
            "programming": ["Python", "C++", "SQL"],
            "databases": ["SQL", "Pinecone", "Milvus", "MongoDB"],
            "tools": ["PyTorch", "TensorFlow", "Docker", "Git", "MLflow", "Hugging Face", "CUDA"],
            "concepts": ["Deep Learning", "Neural Networks", "NLP", "Computer Vision", "LLMs", "Vector Databases", "MLOps"]
        },
        "courses": [
            {"name": "Deep Learning Specialization", "platform": "DeepLearning.AI / Coursera", "link": "https://www.coursera.org/specializations/deep-learning"},
            {"name": "Natural Language Processing Specialization", "platform": "DeepLearning.AI / Coursera", "link": "https://www.coursera.org/specializations/natural-language-processing-tensorflow-pytorch"},
            {"name": "Machine Learning Zoomcamp", "platform": "DataTalks.Club", "link": "https://datatalks.club/courses/ml-zoomcamp.html"}
        ],
        "certifications": [
            "TensorFlow Developer Certificate",
            "AWS Certified Machine Learning - Specialty",
            "Google Cloud Professional Machine Learning Engineer"
        ],
        "placement_tips": [
            "Contribute to open-source AI frameworks or ML projects on GitHub.",
            "Replicate recent AI research papers and share your code implementation.",
            "Understand ML model pipelines, hardware constraints (CPUs vs. GPUs), and inference optimization (TensorRT, quantization).",
            "Prepare for rigorous mathematical questions regarding gradients, loss functions, and weights initialization."
        ],
        "higher_studies": "An MS or Ph.D. in Artificial Intelligence, Machine Learning, or Cognitive Science is highly advantageous due to the research-focused nature of the field.",
        "internships": "Look for Machine Learning Intern, Research Intern, or Computer Vision / NLP Intern positions."
    },
    "web_developer": {
        "title": "Web Developer (Full Stack)",
        "description": "Web Developers design and build website layouts, templates, and backend logic. They construct web applications using client-side frameworks (frontend) and server-side scripts & database systems (backend).",
        "roadmap": [
            {"phase": "Phase 1: Frontend Basics", "details": "Master HTML5, CSS3 (Flexbox/Grid, Responsive Design), and Vanilla JavaScript (ES6+, DOM Manipulation, Async/Fetch)."},
            {"phase": "Phase 2: Modern Frontend Frameworks", "details": "Learn React.js, Vue.js, or Angular. Master state management (Redux, Context API) and styling preprocessors/libraries (Sass, Tailwind CSS)."},
            {"phase": "Phase 3: Backend Foundations", "details": "Learn Node.js with Express, Python with Flask/Django, or Ruby on Rails. Understand server architectures, request-response lifecycles, and middleware."},
            {"phase": "Phase 4: Databases & Auth", "details": "Learn relational databases (PostgreSQL) and document stores (MongoDB). Implement User Authentication (JWT, OAuth, Sessions) and secure APIs."},
            {"phase": "Phase 5: Advanced & Deployment", "details": "Learn SSR (Next.js), Deployment (Vercel, Netlify, Render, AWS), Testing (Jest, Cypress), and basic performance optimization."}
        ],
        "skills": {
            "programming": ["JavaScript", "TypeScript", "HTML/CSS", "Python", "SQL"],
            "databases": ["MongoDB", "PostgreSQL", "MySQL", "Redis"],
            "tools": ["Git", "npm/yarn", "VS Code", "Postman", "Webpack", "Vite"],
            "concepts": ["Responsive Design", "RESTful APIs", "State Management", "Authentication", "Server-Side Rendering", "Web Security"]
        },
        "courses": [
            {"name": "The Web Developer Bootcamp", "platform": "Udemy / Colt Steele", "link": "https://www.udemy.com/"},
            {"name": "Full Stack Open", "platform": "University of Helsinki", "link": "https://fullstackopen.com/en/"},
            {"name": "Meta Front-End/Back-End Developer Certificates", "platform": "Meta / Coursera", "link": "https://www.coursera.org/"}
        ],
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "MongoDB Certified Developer Associate",
            "Meta Full-Stack Developer Certificate"
        ],
        "placement_tips": [
            "Deploy 3 responsive web apps using a backend server and database, and host them live.",
            "Optimize web performance (Lighthouse scores, image compression, lazy loading) and document it.",
            "Study CSS Layouts and JavaScript interview fundamentals (closures, prototypes, event loop).",
            "Practice writing clean REST API specifications."
        ],
        "higher_studies": "Consider a Master's degree in Software Engineering or Web Technologies, though self-study and an outstanding portfolio are often sufficient in this field.",
        "internships": "Look for Frontend Intern, Backend Intern, or Full Stack Web Developer Intern roles on Glassdoor, Indeed, and startups."
    }
}

# Skill Assessment Quiz Questions
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Which of these activities sounds most exciting to you?",
        "options": [
            {"text": "Designing a user interface and making it interactive", "scores": {"web_dev": 3, "software_dev": 1}},
            {"text": "Solving complex logic puzzles and writing algorithms", "scores": {"software_dev": 3, "ai_ml": 2}},
            {"text": "Analyzing graphs and finding patterns in massive datasets", "scores": {"data_science": 3, "ai_ml": 1}},
            {"text": "Finding security gaps, testing networks, and securing data", "scores": {"cybersecurity_analyst": 3}}
        ]
    },
    {
        "id": 2,
        "question": "What is your preferred programming language or what would you like to master?",
        "options": [
            {"text": "JavaScript / HTML / CSS", "scores": {"web_dev": 3, "software_dev": 1}},
            {"text": "Python / R (Data analysis focus)", "scores": {"data_science": 3, "ai_ml": 2}},
            {"text": "C++ / Java (Systems/Desktop applications)", "scores": {"software_dev": 3, "ai_ml": 1}},
            {"text": "Bash / Powershell / Python (Automation/Systems)", "scores": {"cybersecurity_analyst": 3, "software_dev": 1}}
        ]
    },
    {
        "id": 3,
        "question": "How do you feel about high-level mathematics (Calculus, Statistics, Probability)?",
        "options": [
            {"text": "I love it and want to use mathematical theory in my work", "scores": {"ai_ml": 3, "data_science": 2}},
            {"text": "I like statistics and data visualization, but not intense calculus", "scores": {"data_science": 3, "web_dev": 1}},
            {"text": "I prefer logical reasoning and discrete structures, not calculus/statistics", "scores": {"software_dev": 3, "cybersecurity_analyst": 1}},
            {"text": "I want to avoid complex math and focus on protocols or building products", "scores": {"web_dev": 3, "cybersecurity_analyst": 2}}
        ]
    },
    {
        "id": 4,
        "question": "If you were building an application, what part would you focus on?",
        "options": [
            {"text": "The design, layouts, buttons, and responsive responsiveness", "scores": {"web_dev": 3}},
            {"text": "The backend server logic, system architecture, and optimization", "scores": {"software_dev": 3, "web_dev": 2}},
            {"text": "The machine learning brain that makes recommendations", "scores": {"ai_ml": 3, "data_science": 2}},
            {"text": "Ensuring the API, server, and logs are secure against hackers", "scores": {"cybersecurity_analyst": 3, "software_dev": 1}}
        ]
    },
    {
        "id": 5,
        "question": "What kind of projects would you like to show off in your portfolio?",
        "options": [
            {"text": "A beautiful social network website with smooth animations", "scores": {"web_dev": 3, "software_dev": 1}},
            {"text": "A desktop game, compiler, or high-performance search engine", "scores": {"software_dev": 3}},
            {"text": "An image classifier or an AI chatbot based on LLMs", "scores": {"ai_ml": 3, "data_science": 1}},
            {"text": "A secure network topology map or vulnerability scan report", "scores": {"cybersecurity_analyst": 3}}
        ]
    },
    {
        "id": 6,
        "question": "Choose the headline that describes your dream workplace role:",
        "options": [
            {"text": "Constructing beautiful, interactive platforms for consumers", "scores": {"web_dev": 3}},
            {"text": "Architecting reliable, scalable backend computing systems", "scores": {"software_dev": 3, "web_dev": 1}},
            {"text": "Harnessing statistical data to predict customer trends", "scores": {"data_science": 3}},
            {"text": "Guarding critical server frameworks from cyber intrusions", "scores": {"cybersecurity_analyst": 3}}
        ]
    },
    {
        "id": 7,
        "question": "When troubleshooting a bug, what is your style?",
        "options": [
            {"text": "Check browser developer tools, CSS styling rules, or JavaScript console logs", "scores": {"web_dev": 3}},
            {"text": "Trace algorithm parameters in a debugger to find memory or logic leaks", "scores": {"software_dev": 3, "ai_ml": 1}},
            {"text": "Run log queries, inspect packets using Wireshark, or read Linux syslog alerts", "scores": {"cybersecurity_analyst": 3}},
            {"text": "Plot distributions, inspect bias-variance charts, or review accuracy metrics", "scores": {"data_science": 3, "ai_ml": 2}}
        ]
    },
    {
        "id": 8,
        "question": "Which topic of study sounds most fascinating to you?",
        "options": [
            {"text": "Neural network layers and optimization solvers", "scores": {"ai_ml": 3, "data_science": 1}},
            {"text": "Cryptography protocols and penetration strategies", "scores": {"cybersecurity_analyst": 3}},
            {"text": "State management libraries and SEO optimizations", "scores": {"web_dev": 3}},
            {"text": "Distributed system scaling and concurrency models", "scores": {"software_dev": 3}}
        ]
    }
]

def evaluate_quiz(answers):
    """
    Evaluates quiz answers and returns recommended career.
    answers: dict like { "1": 0, "2": 2, ... } mapping question index (str) to selected option index (int)
    """
    scores = {
        "software_developer": 0,
        "data_scientist": 0,
        "cybersecurity_analyst": 0,
        "ai_ml_engineer": 0,
        "web_developer": 0
    }
    
    for q_id_str, opt_idx in answers.items():
        try:
            q_id = int(q_id_str)
            opt_idx = int(opt_idx)
            
            # Find the question
            question = next((q for q in QUIZ_QUESTIONS if q["id"] == q_id), None)
            if not question:
                continue
            
            if 0 <= opt_idx < len(question["options"]):
                option = question["options"][opt_idx]
                for career_key, value in option["scores"].items():
                    # Map quiz keys to full career dictionary keys
                    if career_key == "web_dev":
                        scores["web_developer"] += value
                    elif career_key == "software_dev":
                        scores["software_developer"] += value
                    elif career_key == "data_science":
                        scores["data_scientist"] += value
                    elif career_key == "cybersecurity_analyst":
                        scores["cybersecurity_analyst"] += value
                    elif career_key == "ai_ml":
                        scores["ai_ml_engineer"] += value
        except (ValueError, IndexError):
            continue
            
    # Find career with the highest score
    recommended_career = max(scores, key=scores.get)
    return recommended_career, scores

def call_groq_api(message, history=None):
    """Calls the Groq completions API to answer career-related questions."""
    if not GROQ_API_KEY:
        return None
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are PathFinder AI, an expert AI Career Guidance Counselor. Your goal is to guide candidates in their career journeys.\n"
        "You specialize in 5 primary tech tracks:\n"
        "1. Software Developer: Systems programming, software architecture, backend dev, OOP, data structures & algorithms.\n"
        "2. Data Scientist: Analytics, statistics, machine learning, data cleaning, processing, databases, and visualization.\n"
        "3. Cybersecurity Analyst: Computer networking, security protocols, firewalls, threat modeling, ethical hacking, SIEM, incident response.\n"
        "4. AI/ML Engineer: Deep learning neural networks, computer vision, NLP, large language models, model training & cloud deployment.\n"
        "5. Web Developer (Full Stack): Frontend designs, HTML/CSS layouts, DOM scripting, frameworks (React/Vue), backend APIs, databases, auth.\n\n"
        "Guidelines:\n"
        "- When asked about roadmaps, required skills, online courses, placement prep, internships, or higher studies for any of these 5 tracks, structure your advice around the standard recommendations but feel free to expand.\n"
        "- Always format your responses in clean, structured Markdown (using headings, lists, bullet points, bold text, and hyperlinks).\n"
        "- Answer open-ended career questions (e.g. 'How do I handle career gaps?' or 'What is the future of prompt engineering?') thoroughly, professionally, and encouragement-focused.\n"
        "- Keep responses concise, clear, and action-oriented."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Process history
    if history:
        # history is a list of dicts: [{'sender': 'user'/'bot', 'message': '...'}]
        # Take the last 6 messages to keep context window clean
        for chat in history[-6:]:
            role = "user" if chat["sender"] == "user" else "assistant"
            messages.append({"role": role, "content": chat["message"]})
            
    # Add current message
    messages.append({"role": "user", "content": message})
    
    data = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=8)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Groq API Error Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Failed to communicate with Groq API: {e}")
        return None

def get_chat_response(message, history=None):
    """
    Analyzes the user's chat message and returns a rich response.
    Tries to call Groq API first, falling back to local rule-based system on failure/lack of API key.
    """
    # 1. Try Groq API
    if GROQ_API_KEY:
        ai_response = call_groq_api(message, history)
        if ai_response:
            return ai_response
            
    # 2. Local Fallback
    msg = message.lower().strip()
    
    # 1. Greetings & general helper queries
    if re.search(r'\b(hi|hello|hey|greetings|hola)\b', msg):
        return (
            "Hello! I am your AI Career Counselor. 🌟 I am here to help you navigate your professional journey. "
            "Here is what I can do for you:\n\n"
            "1. **Suggest a career** based on your interests. Try asking: *'What career should I choose?'* or *'Take the assessment quiz'*.\n"
            "2. **Provide detailed roadmaps** for: *Software Developer, Data Scientist, Cybersecurity Analyst, AI/ML Engineer,* or *Web Developer*.\n"
            "3. **Recommend skills and online courses** for any of these fields.\n"
            "4. **Give placement preparation tips** and guidance on internships.\n"
            "5. **Analyze your resume**! Click the **Resume Analyzer** tab to upload your resume and get a compatibility score and tips.\n\n"
            "How can I help you today?"
        )
        
    if re.search(r'\b(help|how to use|what can you do|capabilities)\b', msg):
        return (
            "I can assist you with your career planning! You can ask me questions like:\n"
            "- *'What is the roadmap for a Data Scientist?'*\n"
            "- *'What skills are needed for AI/ML?'*\n"
            "- *'Suggest courses for Web Development.'*\n"
            "- *'Give me placement preparation tips.'*\n"
            "- *'Tell me about cybersecurity internships.'*\n\n"
            "Or use the tabs to take the **Career Assessment Quiz** or upload your resume for analysis!"
        )

    # 2. Roadmap queries
    roadmap_match = re.search(r'\b(roadmap|path|steps|how to become)\b', msg)
    if roadmap_match:
        for key, data in CAREER_DATA.items():
            # Match career keywords
            pattern = key.replace('_', ' ')
            if re.search(r'\b(' + pattern.split()[0] + r')\b', msg) or (key == "web_developer" and "web" in msg) or (key == "ai_ml_engineer" and ("ai" in msg or "ml" in msg or "machine learning" in msg)):
                response = f"### 🗺️ Career Roadmap for {data['title']}\n\n{data['description']}\n\n"
                for step in data['roadmap']:
                    response += f"**{step['phase']}**\n{step['details']}\n\n"
                return response
        
        # If they just asked for 'roadmap' without specifying, list options
        return (
            "Which career roadmap would you like to see? I have detailed roadmaps for:\n"
            "- **Software Developer**\n"
            "- **Data Scientist**\n"
            "- **Cybersecurity Analyst**\n"
            "- **AI/ML Engineer**\n"
            "- **Web Developer**\n\n"
            "Please ask: *'Show me the roadmap for [Career Name]'*."
        )

    # 3. Skills queries
    skills_match = re.search(r'\b(skills|skill|what should i learn|technologies|languages)\b', msg)
    if skills_match:
        for key, data in CAREER_DATA.items():
            pattern = key.replace('_', ' ')
            if re.search(r'\b(' + pattern.split()[0] + r')\b', msg) or (key == "web_developer" and "web" in msg) or (key == "ai_ml_engineer" and ("ai" in msg or "ml" in msg or "machine learning" in msg)):
                skills = data['skills']
                response = f"### 🛠️ Core Skills for {data['title']}\nTo excel in this role, focus on mastering the following:\n\n"
                response += f"- **Programming Languages**: {', '.join(skills['programming'])}\n"
                response += f"- **Databases**: {', '.join(skills['databases'])}\n"
                response += f"- **Tools & Platforms**: {', '.join(skills['tools'])}\n"
                response += f"- **Core Concepts**: {', '.join(skills['concepts'])}\n"
                return response
        
        return (
            "I can list the core skills for the following roles:\n"
            "- **Software Developer**\n"
            "- **Data Scientist**\n"
            "- **Cybersecurity Analyst**\n"
            "- **AI/ML Engineer**\n"
            "- **Web Developer**\n\n"
            "For example, ask: *'What skills are needed for a Software Developer?'*"
        )

    # 4. Courses and certifications queries
    course_match = re.search(r'\b(course|courses|certification|certifications|certify|learn online|study material)\b', msg)
    if course_match:
        for key, data in CAREER_DATA.items():
            pattern = key.replace('_', ' ')
            if re.search(r'\b(' + pattern.split()[0] + r')\b', msg) or (key == "web_developer" and "web" in msg) or (key == "ai_ml_engineer" and ("ai" in msg or "ml" in msg or "machine learning" in msg)):
                response = f"### 📚 Recommended Courses & Certifications for {data['title']}\n\n"
                response += "**Online Courses:**\n"
                for course in data['courses']:
                    response += f"- [{course['name']}]({course['link']}) ({course['platform']})\n"
                response += "\n**Industry Certifications:**\n"
                for cert in data['certifications']:
                    response += f"- {cert}\n"
                return response
        
        return (
            "I can recommend online courses and professional certifications for:\n"
            "- **Software Developer**\n"
            "- **Data Scientist**\n"
            "- **Cybersecurity Analyst**\n"
            "- **AI/ML Engineer**\n"
            "- **Web Developer**\n\n"
            "Try asking: *'Recommend courses for AI/ML Engineer'*."
        )

    # 5. Placement preparation queries
    placement_match = re.search(r'\b(placement|interview|prepare|preparation|resume tips|mock interview|placement tips|job prep)\b', msg)
    if placement_match:
        # Check if they asked for a specific role
        for key, data in CAREER_DATA.items():
            pattern = key.replace('_', ' ')
            if re.search(r'\b(' + pattern.split()[0] + r')\b', msg) or (key == "web_developer" and "web" in msg) or (key == "ai_ml_engineer" and ("ai" in msg or "ml" in msg or "machine learning" in msg)):
                response = f"### 💼 Placement & Interview Tips for {data['title']}\n\n"
                for tip in data['placement_tips']:
                    response += f"- {tip}\n"
                return response
        
        # General placement preparation response
        return (
            "### 💼 General Placement Preparation Tips\n\n"
            "1. **Core Fundamentals**: Ensure you have strong command over Data Structures, Algorithms, and Object-Oriented Programming, regardless of your role.\n"
            "2. **Aptitude & Reasoning**: Companies often start with an online screening round testing quantitative aptitude, logical reasoning, and basic coding.\n"
            "3. **Resume Quality**: Keep your resume to 1 page, use the Harvard format, include links to your GitHub and active portfolio sites, and highlight measurable achievements (e.g., 'Improved database query response by 30%').\n"
            "4. **Mock Interviews**: Practice coding out loud. Explain your logic as you write the code.\n\n"
            "For role-specific tips, ask: *'How to prepare for Data Scientist interviews?'*"
        )

    # 6. Higher Studies & Internships queries
    studies_internships_match = re.search(r'\b(higher studies|masters|mtech|ms|phd|grad school|internship|internships|intern)\b', msg)
    if studies_internships_match:
        # Check if specific role is requested
        for key, data in CAREER_DATA.items():
            pattern = key.replace('_', ' ')
            if re.search(r'\b(' + pattern.split()[0] + r')\b', msg) or (key == "web_developer" and "web" in msg) or (key == "ai_ml_engineer" and ("ai" in msg or "ml" in msg or "machine learning" in msg)):
                response = f"### 🎓 Academic & Internship Path for {data['title']}\n\n"
                response += f"**Internship Opportunities:**\n{data['internships']}\n\n"
                response += f"**Higher Studies Advice:**\n{data['higher_studies']}\n"
                return response
        
        return (
            "### 🎓 Internships & Higher Studies Overview\n\n"
            "**For Internships:**\n"
            "- **When to apply**: Start looking during your pre-final year (3rd year for 4-year degrees).\n"
            "- **Platforms**: Use LinkedIn, Indeed, Internshala, and Wellfound (formerly AngelList).\n"
            "- **Open Source**: Participate in Google Summer of Code (GSoC) or Outreachy to build real-world experience.\n\n"
            "**For Higher Studies:**\n"
            "- **Tech Specializations**: A Master's degree (MS/M.Tech) helps in getting specialized roles like AI/ML research, VLSI engineering, or advanced security analytics.\n"
            "- **Preparation**: Prepare for GRE/TOEFL (for studies abroad) or GATE (for India IITs/NITs) at least 1 year in advance.\n\n"
            "For specific career fields, try: *'What are the internship options in Cybersecurity?'* or *'Should I do a Master's for AI/ML?'*"
        )

    # 7. Interest keywords mapping (rule-based matching to career suggestion)
    interest_map = [
        {"regex": r'\b(design|creative|layouts|front|frontend|ui|ux|website|html|css|javascript)\b', "career": "web_developer", "reason": "interest in building web pages, styling layouts, and designing interactive UI"},
        {"regex": r'\b(math|statistics|data|probability|charts|graphs|mining|datasets|excel|tableau)\b', "career": "data_scientist", "reason": "interest in mathematical theory, data analysis, statistics, and pattern visualization"},
        {"regex": r'\b(neural|learning|tensorflow|pytorch|models|intelligence|ai|ml|prediction|robots|vision|nlp)\b', "career": "ai_ml_engineer", "reason": "fascination with artificial intelligence, deep neural networks, and model training"},
        {"regex": r'\b(hacking|security|cyber|network|firewall|cryptography|protect|breach|penetration|malware)\b', "career": "cybersecurity_analyst", "reason": "interest in computer networks, ethical hacking, digital security, and defense tactics"},
        {"regex": r'\b(code|coding|programming|algorithms|logic|software|c\+\+|java|backend|databases)\b', "career": "software_developer", "reason": "passion for coding, solving logical algorithm problems, and building stable applications"}
    ]
    
    for item in interest_map:
        if re.search(item["regex"], msg):
            career = CAREER_DATA[item["career"]]
            return (
                f"Based on your interest in **{item['reason']}**, a great career path for you might be **{career['title']}**! 🚀\n\n"
                f"**About the role:** {career['description']}\n\n"
                f"Would you like to see the skills required or a roadmap? Ask me: *'What are the skills for {career['title']}?'* or *'Show me the roadmap for {career['title']}'*."
            )
            
    # Suggest assessment quiz if they are totally unsure
    if re.search(r'\b(career path|career|choose|don\'t know|not sure|confused|options|guidance)\b', msg):
        return (
            "It is completely normal to be unsure about your career path! 🤔\n\n"
            "I highly recommend taking our dynamic **Skill Assessment Quiz**! It takes about 2 minutes and will map your answers "
            "to 5 high-demand tech tracks to recommend the best match.\n\n"
            "Click on the **Career Assessment Quiz** tab in the sidebar to get started! "
            "Alternatively, upload your resume to the **Resume Analyzer** to see what you are currently qualified for."
        )

    # 8. Fallback
    return (
        "I'm not sure I fully understood your query, but I want to help! 🔍\n\n"
        "Try asking me about:\n"
        "- **Roadmaps**: *'Show me the Software Developer roadmap.'*\n"
        "- **Skills**: *'What skills are required for Data Science?'*\n"
        "- **Courses**: *'Suggest cybersecurity courses.'*\n"
        "- **Interview Prep**: *'Give me placement tips.'*\n"
        "- **Academic guidance**: *'Higher studies in AI/ML.'*\n\n"
        "Or use the sidebar to take the **Career Assessment Quiz** or upload your resume!"
    )

def analyze_resume(file_path):
    """
    Parses a resume file (.txt or .pdf), extracts text, maps keywords against 
    the 5 career paths, calculates compatibility score, identifies missing skills,
    and returns a detailed JSON-like report.
    """
    text = ""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 1. Text Extraction
    try:
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif file_ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        else:
            return {"error": "Unsupported file format. Please upload a .txt or .pdf resume."}
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}
        
    if not text.strip():
        return {"error": "Could not extract text from the file. Please ensure it is not scanned or empty."}
        
    text_lower = text.lower()
    
    # Define mapping of careers to exact match keywords
    career_keywords = {
        "software_developer": [
            "java", "c++", "c#", "go ", "golang", "data structures", "algorithms", "oop", "object oriented",
            "git ", "github", "docker", "kubernetes", "system design", "rest api", "sql", "testing", "junit", "ci/cd"
        ],
        "data_scientist": [
            "python", "r ", "sql", "pandas", "numpy", "matplotlib", "seaborn", "scikit", "tableau", "power bi",
            "statistics", "probability", "regression", "clustering", "data analysis", "data cleaning", "big data", "spark"
        ],
        "cybersecurity_analyst": [
            "networking", "tcp/ip", "dns", "firewall", "vpn", "cryptography", "wireshark", "splunk", "nmap", 
            "security+", "cissp", "oscp", "penetration testing", "incident response", "ethical hacking", "siem", "vulnerability"
        ],
        "ai_ml_engineer": [
            "tensorflow", "pytorch", "keras", "deep learning", "neural network", "computer vision", "nlp", 
            "natural language processing", "linear algebra", "calculus", "machine learning", "hugging face", "transformers", "llm"
        ],
        "web_developer": [
            "html", "css", "javascript", "react", "node", "express", "mongodb", "angular", "vue", "typescript", 
            "bootstrap", "tailwind", "responsive design", "web development", "full stack", "frontend", "backend"
        ]
    }
    
    # Calculate matches
    matched_skills_map = {}
    missing_skills_map = {}
    match_scores = {}
    
    for career_key, keywords in career_keywords.items():
        matched = []
        missing = []
        for kw in keywords:
            # Check keyword match using regex (word bounds for short words like r, git, go)
            if kw.endswith(' '):
                # Search with trailing space/word bound
                pattern = r'\b' + re.escape(kw.strip()) + r'\b'
            else:
                pattern = re.escape(kw)
                
            if re.search(pattern, text_lower):
                matched.append(kw.strip())
            else:
                missing.append(kw.strip())
                
        matched_skills_map[career_key] = matched
        missing_skills_map[career_key] = missing
        
        # Calculate matching score percentage
        score = int((len(matched) / len(keywords)) * 100)
        match_scores[career_key] = score

    # Find the career with the highest match score (primary match)
    primary_career = max(match_scores, key=match_scores.get)
    primary_career_data = CAREER_DATA[primary_career]
    
    # Format and return analysis report
    analysis_result = {
        "primary_career_key": primary_career,
        "primary_career_title": primary_career_data["title"],
        "match_score": match_scores[primary_career],
        "matched_skills": matched_skills_map[primary_career],
        "missing_skills": missing_skills_map[primary_career],
        "all_scores": {CAREER_DATA[k]["title"]: match_scores[k] for k in match_scores},
        "recommendations": {
            "courses": primary_career_data["courses"],
            "certifications": primary_career_data["certifications"],
            "prep_tips": primary_career_data["placement_tips"]
        }
    }
    
    return analysis_result
