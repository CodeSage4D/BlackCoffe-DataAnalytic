import os
import pandas as pd
from textblob import TextBlob
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import syllapy

# Ensure necessary NLTK data is downloaded
nltk.download("punkt")

# Function to load words from a file
def load_words(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        words = set(word.strip().lower() for word in file.readlines())
    return words

# Function to load stopwords from a directory
def load_stopwords(directory):
    stopwords = set()
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            stopwords.update(load_words(file_path))
    return stopwords

# Load positive and negative words
positive_words = load_words("MasterDictionary/positive-words.txt")
negative_words = load_words("MasterDictionary/negative-words.txt")

# Load stopwords
stopwords = load_stopwords("StopWords")

# Function to compute text analysis scores
def compute_scores(text):
    # Tokenize text
    words = word_tokenize(text)
    sentences = sent_tokenize(text)

    # Filter out stopwords
    words = [word for word in words if word.lower() not in stopwords]

    # Initialize TextBlob for sentiment analysis
    blob = TextBlob(" ".join(words))

    # Custom sentiment analysis using the loaded positive and negative words
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)

    # Calculations
    word_count = len(words)
    sentence_count = len(sentences)
    avg_sentence_length = word_count / sentence_count if sentence_count != 0 else 0
    complex_word_count = sum(1 for word in words if syllapy.count(word) > 2)
    percentage_complex_words = (complex_word_count / word_count) * 100 if word_count != 0 else 0
    syllable_counts = [syllapy.count(word) for word in words]
    syllable_per_word = sum(syllable_counts) / word_count if word_count != 0 else 0
    personal_pronouns = sum(1 for word in words if word.lower() in ["i", "we", "my", "ours", "us"])
    avg_word_length = sum(len(word) for word in words) / word_count if word_count != 0 else 0

    # FOG Index Calculation
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    
    # Average Words Per Sentence
    avg_words_per_sentence = word_count / sentence_count if sentence_count != 0 else 0

    return {
        "POSITIVE SCORE": positive_score,
        "NEGATIVE SCORE": negative_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVITY SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": avg_sentence_length,
        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,
        "COMPLEX WORD COUNT": complex_word_count,
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": syllable_per_word,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_length,
    }

# Initialize list to store output data
output_data = []

# Check if "Output Datastructure.xlsx" file exists
datastructure_file = "Output Data Structure.xlsx"
if not os.path.exists(datastructure_file):
    raise FileNotFoundError(f"{datastructure_file} file not found. Please make sure the file is present in the script directory.")

# Read the existing "Output Datastructure.xlsx" file
datastructure_df = pd.read_excel(datastructure_file)

# Extract URL_ID and URL columns
url_data = datastructure_df[["URL_ID", "URL"]]

# Read and analyze each extracted article
for file_name in os.listdir("extracted_articles"):
    if file_name.endswith(".txt"):
        file_path = os.path.join("extracted_articles", file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                scores = compute_scores(text)
                url_id = file_name.split(".")[0]
                scores["URL_ID"] = url_id
                output_data.append(scores)
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")

# Convert output data to DataFrame
output_df = pd.DataFrame(output_data)

# Merge the extracted data with the URL data
merged_df = pd.merge(url_data, output_df, left_on="URL_ID", right_on="URL_ID", how="left")

# Ensure any existing file is deleted
output_file = "Output_Data.xlsx"
if os.path.exists(output_file):
    os.remove(output_file)

# Save the output data to an Excel file
merged_df.to_excel(output_file, index=False)

# Print a success message
print("Data processing completed successfully and saved to Output_Data.xlsx")
