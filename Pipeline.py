import time
from newspaper import Article
import spacy
import re
from collections import defaultdict
import textwrap

# Load the spaCy English model (or your trained model if available)
nlp = spacy.load('en_core_web_sm')

# Define list of news article URLs
urls = [
    
    '',
]

# Define trigger words mapped by event category
category_mapping = {
    "Announcement": ["announced", "introduced", "unveiled", "declared"],
    "Legislation": ["passed", "debated", "reviewed", "rejected", "voted","vote"],
    "Protest": ["protested", "sit-in", "striked"],
    "Policy Action": ["legislation", "policy", "approval","plan"],
    "Crisis": ["emergency", "imposed", "urgent"],
    "Implementation": ["implemented", "enforced", "issued", "guideline", "regulation"],
    "Directive": ["order", "issuance"],
    "Consultation": ["consultation"],
    "Agreement": ["signed", "agreed", "treaty"],
    "Judicial": ["ruled", "challenged", "appealed"],
    "Research and Reporting": ["poll", "report", "study"]
}
# Flatten all trigger words for annotation purposes
all_triggers = [word for keywords in category_mapping.values() for word in keywords]
trigger_pattern = re.compile(r'\b(?:' + '|'.join(all_triggers) + r')\b', re.IGNORECASE)

# Helper function to extract arguments using dependency parsing (unchanged)
def extract_arguments(doc):
    arguments = {
        "Actor": [],
        "Action": [],
        "Target": [],
        "Location": [],
        "Time": []
    }
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass") and token.ent_type_ in ("PERSON", "ORG", "GPE"):
            arguments["Actor"].append(token.text)
        if token.pos_ == "VERB" and trigger_pattern.search(token.text):
            arguments["Action"].append(token.lemma_)
        if token.dep_ == "dobj":
            arguments["Target"].append(token.text)
        if token.ent_type_ in ("GPE", "LOC"):
            arguments["Location"].append(token.text)
        if token.ent_type_ in ("DATE", "TIME"):
            arguments["Time"].append(token.text)
    for key in arguments:
        arguments[key] = list(set(arguments[key]))
    return arguments

# Function to perform sentence tokenization using spaCy
def custom_sent_tokenize_spacy(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]

# Function to annotate a sentence with trigger words.
# For each token that is a trigger, try to find its subject (nsubj/nsubjpass) that is a PERSON, ORG, or GPE.
def annotate_sentence_with_subject(sentence):
    doc = nlp(sentence)
    annotated_tokens = []
    for token in doc:
        # Check if token (in lowercase) is one of our triggers
        if token.text.lower() in [t.lower() for t in all_triggers]:
            subj = None
            # Look for subject in token's children
            for child in token.children:
                if child.dep_ in ("nsubj", "nsubjpass") and child.ent_type_ in ("PERSON", "ORG", "GPE"):
                    subj = child.text
                    break
            # If not found, check the token's head (if not the token itself)
            if not subj and token.head != token:
                if token.head.dep_ in ("nsubj", "nsubjpass") and token.head.ent_type_ in ("PERSON", "ORG", "GPE"):
                    subj = token.head.text
            if subj:
                annotated_tokens.append(f"{token.text}** (said by {subj})")
            else:
                annotated_tokens.append(f"{token.text}")
        else:
            annotated_tokens.append(token.text)
    # Reconstruct sentence. (Note: This simple join may not handle punctuation perfectly.)
    return " ".join(annotated_tokens)

# Function to truncate text to a specified length without cutting off words
def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text
    else:
        return textwrap.shorten(text, width=max_length, placeholder="...")

# Function to categorize the event based on trigger words found in the article text
def categorize_event(text):
    triggers = trigger_pattern.findall(text)
    if not triggers:
        return "None"

    triggers = [t.lower() for t in triggers]
    cat_counts = defaultdict(int)
    first_trigger_cat = None
    for t in triggers:
        for category, keywords in category_mapping.items():
            if t in keywords:
                cat_counts[category] += 1
                if first_trigger_cat is None:
                    first_trigger_cat = category
    if not cat_counts:
        return "None"
    if len(triggers) == 1:
        return first_trigger_cat
    max_count = max(cat_counts.values())
    candidate_categories = [cat for cat, count in cat_counts.items() if count == max_count]
    if len(candidate_categories) > 1:
        for t in triggers:
            for category, keywords in category_mapping.items():
                if t in keywords and category in candidate_categories:
                    return category
    else:
        return candidate_categories[0]
    return "None"

def event_extract(url, max_event_sentences=2, max_annotated_length=500):
    article = Article(url)
    article.download()
    article.parse()

    sentences = custom_sent_tokenize_spacy(article.text)
    trigger_sentences = [sent for sent in sentences if trigger_pattern.search(sent)]

    if trigger_sentences:
        annotated_sentences = [annotate_sentence_with_subject(sent) for sent in trigger_sentences[:max_event_sentences]]
        annotated_text = ' '.join(annotated_sentences)
        annotated_text = truncate_text(annotated_text, max_annotated_length)
        event_category = categorize_event(article.text)
    else:
        annotated_text = "No specific event mentioned"
        event_category = "None"

    extracted_triggers = list(set(trigger_pattern.findall(article.text)))
    if extracted_triggers and annotated_text != "No specific event mentioned":
        annotated_text += "\n\nTriggers: " + ", ".join(extracted_triggers)

    doc = nlp(article.text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    arguments = extract_arguments(doc)

    publish_date = article.publish_date
    if not publish_date:
        date_entities = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        publish_date = date_entities[0] if date_entities else "Unknown"

    # Instead of printing, let's RETURN a dict with the extracted info:
    return {
        "title": article.title,
        "publication_date": str(publish_date),
        "event_category": event_category,
        "annotated_text": annotated_text,
        "url": article.url,
       
    }

# IMPORTANT:
# Comment out or remove the loop that processes your hard-coded URLs:
# for url in urls:
#     event_extract(url)