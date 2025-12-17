import re
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------- PDF TEXT EXTRACTION --------
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


# -------- TEXT CLEANING --------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


# -------- RESUME–JD MATCH --------
def calculate_match(resume_text, jd_text):
    documents = [resume_text, jd_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    feature_names = vectorizer.get_feature_names_out()
    resume_vector = tfidf_matrix[0].toarray()[0]
    jd_vector = tfidf_matrix[1].toarray()[0]

    matched = []
    missing = []

    for i in range(len(feature_names)):
        if jd_vector[i] > 0 and resume_vector[i] > 0:
            matched.append(feature_names[i])
        elif jd_vector[i] > 0 and resume_vector[i] == 0:
            missing.append(feature_names[i])

    return round(similarity * 100, 2), matched, missing


# -------- ROLE RECOMMENDATION --------
def recommend_best_role(resume_text):
    role_profiles = {
        "Data Analyst":
            "python sql data analysis pandas numpy matplotlib statistics "
            "machine learning data preprocessing exploratory data analysis "
            "research reporting visualization",

        "Business Analyst":
            "business analysis stakeholder requirements documentation "
            "reporting communication decision making",

        "HR / Talent Acquisition":
            "recruitment hiring onboarding hr operations communication",

        "Web Developer":
            "html css javascript react django flask web development",

        "Operations / Coordinator":
            "operations coordination scheduling reporting process management"
    }

    roles = list(role_profiles.keys())
    documents = [resume_text] + list(role_profiles.values())

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    best_index = similarities.argmax()
    best_role = roles[best_index]
    best_score = round(similarities[best_index] * 100, 2)

    return best_role, best_score
