"""
Extract follow-up questions and challenges from CSV feedback columns.
Merges with existing follow-up-questions.json.
"""

import json
import pandas as pd
import re

def load_existing_questions():
    """Load existing follow-up questions."""
    try:
        with open("data/follow-up-questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def extract_questions_from_text(text, reviewer_name, section_name):
    """Extract questions and challenges from feedback text."""
    if pd.isna(text) or not str(text).strip():
        return []
    
    text = str(text).strip()
    questions = []
    
    # Split into sentences (roughly)
    sentences = re.split(r'[.!]\s+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check if it's a question (ends with ?)
        is_question = sentence.endswith('?')
        
        # Check if it contains challenge/action language
        challenge_patterns = [
            r'\bchallenge you\b',
            r'\bI\'d like to (see|hear|understand|know)\b',
            r'\bI would like to (see|hear|understand|know)\b',
            r'\bwhat will you\b',
            r'\bwhen will you\b',
            r'\bhow will you\b',
            r'\bwhat are you\b',
            r'\bby what date\b',
            r'\bplease\b.*\b(flush|define|develop|create|provide)\b',
            r'\bmissing is\b',
            r'\bneed to\b',
            r'\bshould\b.*\b(add|include|develop|define)\b',
            r'\bwould have liked\b',
            r'\bwould be good\b',
            r'\bwould be beneficial\b',
            r'\black of\b',
        ]
        
        is_challenge = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in challenge_patterns)
        
        if is_question or is_challenge:
            # Clean up the sentence
            clean_sentence = sentence
            if not clean_sentence.endswith('?') and not clean_sentence.endswith('.'):
                clean_sentence += '.'
            
            questions.append({
                "category": section_name,
                "reviewer": reviewer_name,
                "quote": clean_sentence,
                "source": "CSV Feedback"
            })
    
    return questions

def extract_all_csv_questions():
    """Extract all questions from CSV feedback columns."""
    df = pd.read_csv("data/performance_reviews.csv", low_memory=False)
    
    # Map column names to section names
    section_columns = {
        "Key Projects & Initiatives": "Key Projects & Initiatives",
        "Value Adds & Cost Avoidance": "Value Adds & Cost Avoidance",
        "Cost Savings Delivered": "Cost Savings Delivered",
        "Innovation & Continuous Improvement": "Innovation & Continuous Improvement",
        "Issues, Challenges & Accountability": "Issues, Challenges & Accountability",
        "2026 Forward Strategy & Vision": "2026 Forward Strategy & Vision",
        "Personal Goals & Role Maturity": "Personal Goals & Role Maturity",
        "Executive Presence & Presentation Skills": "Executive Presence & Presentation Skills"
    }
    
    ad_questions = {}
    
    for idx, row in df.iterrows():
        ad_name = str(row.get("Account Director Name", "")).strip()
        reviewer_name = str(row.get("Enter Your Name", "")).strip()
        
        if not ad_name or ad_name == "Account Director Name":
            continue
        
        # Skip joint reviews for now (we'll handle them separately)
        if "/" in ad_name:
            continue
        
        if ad_name not in ad_questions:
            ad_questions[ad_name] = []
        
        # Extract questions from each section's feedback
        for col_name, section_name in section_columns.items():
            if col_name in df.columns:
                feedback = row.get(col_name)
                questions = extract_questions_from_text(feedback, reviewer_name, section_name)
                ad_questions[ad_name].extend(questions)
    
    return ad_questions

def merge_questions(existing, new_csv_questions):
    """Merge existing transcript questions with new CSV questions."""
    merged = {}
    
    # Get all unique AD names
    all_ads = set(existing.keys()) | set(new_csv_questions.keys())
    
    for ad_name in all_ads:
        merged[ad_name] = []
        
        # Add existing questions (from transcripts)
        if ad_name in existing:
            for q in existing[ad_name]:
                # Mark as from transcript if not already marked
                if "source" not in q:
                    q["source"] = "Transcript"
                merged[ad_name].append(q)
        
        # Add new CSV questions (deduplicate by quote)
        if ad_name in new_csv_questions:
            existing_quotes = {q.get("quote", "").lower().strip() for q in merged[ad_name]}
            for q in new_csv_questions[ad_name]:
                quote_lower = q.get("quote", "").lower().strip()
                if quote_lower not in existing_quotes:
                    merged[ad_name].append(q)
    
    return merged

def main():
    print("Loading existing follow-up questions...")
    existing = load_existing_questions()
    
    print("Extracting questions from CSV feedback...")
    csv_questions = extract_all_csv_questions()
    
    print("\nNew CSV questions found:")
    for ad_name, questions in csv_questions.items():
        if questions:
            print(f"  {ad_name}: {len(questions)} questions")
    
    print("\nMerging with existing questions...")
    merged = merge_questions(existing, csv_questions)
    
    print("\nFinal counts:")
    for ad_name, questions in sorted(merged.items()):
        print(f"  {ad_name}: {len(questions)} total questions")
    
    print("\nSaving updated follow-up-questions.json...")
    with open("data/follow-up-questions.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    print("✅ Done! Updated follow-up-questions.json")

if __name__ == "__main__":
    main()

