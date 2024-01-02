import re
import pdfplumber
import os
import docx2txt
import zipfile  # Used for ignoring zipfile.BadZipFile error
import csv
import subprocess
from striprtf.striprtf import rtf_to_text
from dateutil.parser import parse
import pandas as pd
import time  # 22/09/23 for tracking the time taken to process the files
import spacy


def extract_phone_number(text):
    # Define a pattern to match 10-digit phone numbers with or without spaces and dashes
    phone_pattern = r'(?:(?:\+91)|(?:0)|(?:91))?[789]\d{9}|\d{10}|\d{5}[\s-]\d{5}'

    # Find all matches of 10-digit phone numbers with or without spaces and dashes
    matches = re.findall(phone_pattern, text)

    if matches:
        # Extract the rightmost 10 digits (ignoring spaces and dashes)
        rightmost_digits = [re.sub(r'[\s-]', '', number)[-10:]
                            for number in matches]
        return rightmost_digits[0]
    else:
        return None


def extract_email_from_resume(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)

    if matches:
        # Stop parsing after ".com"
        email = matches[0]
        if '.com' in email:
            return email.split('.com')[0] + '.com'
    return None


def extract_text_from_rtf(rtf_path):
    with open(rtf_path, 'r') as rtf_file:
        rtf_content = rtf_file.read()
        plain_text = rtf_to_text(rtf_content)
        return plain_text


def load_skills_data(csv_file):
    skills_data = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            skills_data.extend(row)
    return skills_data


def load_education_data(csv_file):
    education_data = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            education_data.extend(row)
    return education_data


def load_cities_data(csv_file):
    cities_data = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            cities_data.extend(row)
    return cities_data


def load_states_data(csv_file):
    states_data = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            states_data.extend(row)
    return states_data


def extract_address_from_text(resume_text, cities_data, states_data):
    # Create sets of unique cities and states for faster lookup
    cities_set = set(cities_data)
    states_set = set(states_data)

    # Define a regular expression pattern to match addresses
    address_pattern = r'\b(?:' + '|'.join(map(re.escape,
                                              cities_set | states_set)) + r')\b'

    # Find all matches of cities and states in the resume text
    matches = re.findall(address_pattern, resume_text, flags=re.IGNORECASE)

    # Filter out matches that are also substrings of other matches (e.g., city names contained within state names)
    filtered_matches = []
    for match in matches:
        is_valid = True
        for other_match in matches:
            if match != other_match and match in other_match:
                is_valid = False
                break
        if is_valid:
            filtered_matches.append(match)

    # Convert the list of addresses to a set to remove duplicates, then back to a list
    unique_addresses = list(set(filtered_matches))

    return unique_addresses


def extract_skills_from_text(resume_text, skills_data):
    # Convert the skills data to lowercase for case-insensitive matching
    skills_data_lower = [skill.lower() for skill in skills_data]
    # Split the resume text into words
    words = resume_text.split()
    # Find the intersection of words in the resume and skills data
    skills = list(set(words).intersection(skills_data_lower))
    return skills


def extract_education_from_text(resume_text, education_data):
    # Convert the resume text to lowercase
    resume_text = resume_text.lower()

    extracted_education = []

    for edu_specialization in education_data:
        edu_specialization = edu_specialization.lower()

        # Use word boundaries to match whole words
        pattern = r'\b' + re.escape(edu_specialization) + r'\b'

        # Check if the education specialization is present in the resume text
        if re.search(pattern, resume_text):
            extracted_education.append(edu_specialization)

    return extracted_education


def extract_date_of_birth(resume_text):
    # Define patterns for various date formats
    date_patterns = [
        # Matches date formats like DD/MM/YYYY, DD-MM-YYYY, DD/MM/YY, etc.
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        # Matches date formats like 12th October 2003 or 12 Oct 23
        r'\b\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*\s?\d{2,4}\b',
        # Matches date formats like 12th October 2003 with ordinal suffix or 12 Oct 23
        r'\b\d{1,2}(?:st|nd|rd|th)?\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*\s?\d{2,4}\b',
        # Matches date formats like 12/10/2003 or 12-10-2003 or 12/10/23
        r'\b\d{1,2}[/-]\d{2}[/-]\d{2,4}\b',
        # Matches date formats like 12Oct23
        r'\b\d{1,2}(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*\d{2,4}\b',
        # Matches date formats like 12th octoberober 2003 or 12 october 23
        r'\b\d{1,2}\s?(?:january|feburaryurary|March|april|May|june|july|august|september|october|november|december)[a-zA-Z]*\s?\d{2,4}\b',
        # Matches date formats like 12th octoberober 2003 with ordinal suffix or 12 october 23
        r'\b\d{1,2}(?:st|nd|rd|th)?\s?(?:Jan|feburary|March|april|May|june|july|august|september|october|november|december)[a-zA-Z]*\s?\d{2,4}\b',
        # Matches date formats like 12/10/2003 or 12-10-2003 or 12/10/23
        r'\b\d{1,2}[/-]\d{2}[/-]\d{2,4}\b',
        r'\b\d{1,2}(?:Jan|feburary|March|april|May|june|july|august|september|october|november|december)[a-zA-Z]*\d{2,4}\b',
        r'\b\d{1,2}\s?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-zA-Z]*\s?\d{2,4}\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-zA-Z]*\s?\d{2,4}\b',

    ]

    for date_pattern in date_patterns:
        matches = re.findall(date_pattern, resume_text)
        if matches:
            date_str = matches[0]
            try:
                date_of_birth = parse(date_str, fuzzy=True)
                return date_of_birth.strftime('%d-%b-%Y')
            except ValueError:
                pass

    return None


def extract_name_from_filename(filename):
    # Remove file extension from the filename
    name = os.path.splitext(filename)[0]

    # Get the last part of the path after the last '/'
    name = name.split(os.path.sep)[-1]

    # Remove non-alphabetic characters and numbers within brackets
    name = re.sub(r'\[[^\]]*\]', '', name)
    name = ''.join(filter(lambda c: c.isalpha() or c.isspace(), name))

    # Replace underscores and spaces with hyphens
    name = name.replace('_', '-')
    name = name.replace(' ', '-')

    # Remove leading and trailing hyphens
    name = name.strip('-')

    # Split the name using hyphens
    name_parts = name.split('-')
    name_parts = [part.capitalize()
                  for part in name_parts]  # Capitalize each part

    return '-'.join(name_parts)


def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text


def extract_text_from_docx(docx_path):
    try:
        text = docx2txt.process(docx_path)
        return text
    except Exception as e:
        print(f"Error processing DOCX file '{docx_path}': {str(e)}")
        return ""


def extract_text_from_doc(doc_path):
    try:
        result = subprocess.run(['antiword', doc_path],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error extracting text from '{doc_path}': {result.stderr}")
            return None
    except Exception as e:
        print(f"Error extracting text from '{doc_path}': {str(e)}")
        return None


nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    # Remove multiple consecutive spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple consecutive new lines
    text = re.sub(r'\n+', '\n', text)
    # Remove leading new lines
    text = text.lstrip('\n')
    return text

# Function to extract work experience


def extract_work_experience(text):
    work_experience = []
    doc = nlp(text)

    sentences = list(doc.sents)
    num_sentences = len(sentences)

    for i in range(num_sentences):
        sentence = sentences[i]
        if "work experience" in sentence.text.lower():
            j = i + 1
            while j < num_sentences and not any(keyword in sentences[j].text.lower() for keyword in ["education", "skills", "projects"]):
                # Use .text to get the full sentence
                work_experience.append(sentences[j].text)
                j += 1

    return work_experience


# Function to extract the immediate parent folder name
def extract_parent_folder_name(file_path):
    parent_folder_name = os.path.basename(os.path.dirname(file_path))
    return parent_folder_name


def save_to_excel(data, output_excel_path):
    df = pd.DataFrame(data)
    df.to_excel(output_excel_path, index=False)


def save_to_csv(data, output_csv_path):
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False)


# Specify the input folder path containing files (PDFs, DOCXs, DOCs)
input_folder = input("Enter the path to the folder containing resumes: ")

# Output file path
output_file = "output.txt"
start_time = time.time()  # Get the current time

# List of supported file extensions
supported_extensions = ['.pdf', '.docx', '.doc', '.rtf']
skills_data = load_skills_data('skills.csv')
education_data = load_education_data(
    'education_specialization.csv')  # Load education data
cities_data = load_cities_data('city.csv')
states_data = load_states_data('states.csv')
output_data = []  # Initialize the output_data list before processing
total_files_scanned = 0  # Initialize the counter for total scanned files


def process_folder(folder_path):
    global total_files_scanned
    num_files_scanned = 0
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) and item.lower().endswith(tuple(supported_extensions)):
            process_file(item_path)
            num_files_scanned += 1
            total_files_scanned += 1
        elif os.path.isdir(item_path):
            process_folder(item_path)
    print(f"Scanned {num_files_scanned} files in folder: {folder_path}")


processed_files = set()


def process_file(file_path):
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pdf':
            file_type = 'PDF'
            resume_text = extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            file_type = 'DOCX'
            resume_text = extract_text_from_docx(file_path)
            if not resume_text:
                print(
                    f"Empty or error-prone content in '{file_path}'. Skipping.")
                return
        elif file_extension == '.doc':
            file_type = 'DOC'
            resume_text = extract_text_from_doc(file_path)
        elif file_extension == '.rtf':
            file_type = 'RTF'
            resume_text = extract_text_from_rtf(file_path)
        else:
            return  # Skip unsupported formats

        if resume_text is None:
            print(f"Failed to extract text from '{file_path}'. Skipping.")
            return

        # Convert the resume text to lowercase
        resume_text = resume_text.lower()
        name = extract_name_from_filename(os.path.basename(file_path))
        email = extract_email_from_resume(resume_text)
        phone_number = extract_phone_number(resume_text)
        relative_path = os.path.relpath(file_path, os.getcwd())
        skills = extract_skills_from_text(resume_text, skills_data)
        education_details = extract_education_from_text(
            resume_text, education_data)  # Extract education details
        date_of_birth = extract_date_of_birth(resume_text)
        addresses = extract_address_from_text(
            resume_text, cities_data, states_data)
        work_experience = extract_work_experience(resume_text)

        data = {
            "Index": len(output_data) + 1,
            "File Name": os.path.basename(file_path),
            "Name": name,
            "Email": email if email else "No email found",
            "Number": phone_number if phone_number else "No phone number found",
            "Date of Birth": date_of_birth if date_of_birth else "No date of birth found",
            "Addresses": ', '.join(addresses) if addresses else "No addresses found",
            # Add education details
            "Education Specializations": ', '.join(education_details) if education_details else "No education details found",
            "Skills": ', '.join(skills) if skills else "No skills found",
            "Type": file_type,
            "Folder": relative_path,  # Add the relative path to the data
            "Work Experience": ', '.join(work_experience) if work_experience else "No work experience found"

        }
        output_data.append(data)  # Add the extracted data to the list
    except zipfile.BadZipFile as bad_zip_error:
        print(f"Bad Zip File Error for '{file_path}': {bad_zip_error}")
    except Exception as e:
        print(f"Error processing '{file_path}': {str(e)}")
        print("Skipping this file.")


try:
    # Clear the output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    output_data = []

    process_folder(input_folder)
    print(f"Total files scanned: {total_files_scanned}")

    output_excel_path = "output.xlsx"
    save_to_excel(output_data, output_excel_path)
    print(f"Data saved to {output_excel_path}")

    output_csv_path = "output.csv"
    save_to_csv(output_data, output_csv_path)
    print(f"Data saved to {output_csv_path}")

    with open(output_file, 'w') as output:
        for entry in output_data:
            output.write(f"{entry['Index']})\n")
            output.write(f"    File Name: {entry['File Name']}\n")
            output.write(f"    Name: {entry['Name']}\n")
            output.write(f"    Email: {entry['Email']}\n")
            output.write(f"    Number: {entry['Number']}\n")
            output.write(f"    DateOfBirth: {entry['Date of Birth']}\n")
            # Include education details
            output.write(f"    Address: {entry['Addresses']}\n")
            output.write(f"    Work Experience:\n")
            if entry['Work Experience']:
                cleaned_work_experience = clean_text(entry['Work Experience'])
                for line in cleaned_work_experience.splitlines():
                    cleaned_line = line.strip()
                    if cleaned_line:  # Check if the line is not empty after stripping
                        output.write(f"    {cleaned_line}\n")
            # Include education details
            output.write(
                f"    Education Specializations: {entry['Education Specializations']}\n")
            output.write(f"    Skills: {entry['Skills']}\n")
            output.write(f"    Type: {entry['Type']}\n")
            output.write(f"    Folder: {entry['Folder']}\n\n")

    end_time = time.time()  # Get the current time
    time_taken = end_time - start_time  # Calculate the time taken
    print(f"Time taken: {time_taken} seconds")

except Exception as e:
    print(f"An error occurred: {str(e)}")
