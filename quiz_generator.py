import spacy
from collections import Counter
import random

nlp = spacy.load("en_core_web_sm")

def generate_quiz(text, num_questions=20):
    """
    Generates a quiz from the text of a chapter using spaCy.
    """
    if not text:
        return []

    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    # Ensure the number of questions does not exceed the number of sentences
    num_questions = min(num_questions, len(sentences))

    # Randomly select sentences to form questions
    selected_sentences = random.sample(sentences, num_questions)

    questions = []

    for i, sentence in enumerate(selected_sentences):
        sent_doc = nlp(sentence)
        nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]

        if len(nouns) < 2:
            continue

        noun_counts = Counter(nouns)
        subject = noun_counts.most_common(1)[0][0]

        question_stem = sentence.replace(subject, "______")

        answer_choices = [subject]

        # Add distractors from other nouns in the sentence
        distractors = list(set(nouns) - {subject})
        random.shuffle(distractors)

        # Ensure there are at least three distractors
        while len(distractors) < 3:
            # If not enough distractors from the sentence, pick random nouns from the whole text
            random_noun = random.choice([token.text for token in doc if token.pos_ == "NOUN" and token.text != subject])
            if random_noun not in distractors:
                distractors.append(random_noun)

        for distractor in distractors[:3]:
            answer_choices.append(distractor)

        random.shuffle(answer_choices)

        correct_index = answer_choices.index(subject)

        questions.append({
            "id": f"c1q{i+1}",
            "question": question_stem,
            "options": answer_choices,
            "correct": correct_index,
            "explanation": f"The correct answer is '{subject}'."
        })

    return questions
