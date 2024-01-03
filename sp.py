import spacy

nlp = spacy.load("en_core_web_sm")

def is_follow_up_question(user_input, previous_input):
    # Analyze the current input
    doc = nlp(user_input)
    # Check if it's likely a standalone question
    if any(token.dep_ == "ROOT" and token.pos_ == "VERB" for token in doc):
        return False
    # If no clear verb is present, it might be a follow-up
    return True

# Example usage
user_input = "Show me the details of the first one."
previous_input = "Which are the tickets that had an issue with VPN?"
is_follow_up = is_follow_up_question(user_input, previous_input)
