import os
import sys
import logging
import uuid
import random
import json
import PyPDF2
import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.schema import Document

# Set up logging to reduce unnecessary output
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

# Set up the OpenAI API key
os.environ["OPENAI_API_KEY"] = ""  # Replace with your actual OpenAI API key

# Initialize LLM
llm = OpenAI(model="gpt-4o-mini", temperature=0.1)

# Initialize settings and set chunk size
Settings.llm = llm
Settings.chunk_size = 512  # Adjust chunk size as needed

def process_pdf_to_text(file_path):
    """Read the PDF file and return its text content."""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()
    return full_text

def create_index_from_pdf(file_path, storage_dir="./storage"):
    """Process the PDF and create an index from the document."""
    full_text = process_pdf_to_text(file_path)

    # Create a document object from the PDF text
    document = Document(text=full_text, doc_id=str(uuid.uuid4()))

    # Parse the document into nodes
    nodes = Settings.node_parser.get_nodes_from_documents([document])

    # Initialize storage context (by default it's in-memory)
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)

    # Define Vector Index over the data
    vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

    # Save the index to disk
    vector_index.storage_context.persist(persist_dir=storage_dir)

    print("Index created and saved successfully!")
    return vector_index, nodes

def load_index(storage_dir="./storage"):
    """Load the index from disk."""
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    vector_index = VectorStoreIndex.load(storage_context=storage_context)
    print("Index loaded successfully!")
    return vector_index

def generate_questions_from_nodes(llm, nodes, num_questions):
    """Generate multiple-choice questions from nodes."""
    questions = []
    selected_nodes = random.sample(nodes, min(num_questions, len(nodes)))  # Randomly select nodes

    for node in selected_nodes:
        for attempt in range(3):  # Retry up to 3 times
            prompt = (
                f"Generate a multiple-choice question from the following text:\n"
                f"{node.text}\n"+'''
                Make sure to provide the response in the following strict JSON format:
                {
                "question": "question goes here",
                "options" : {
                "option 1":"...",
                "option 2": "...",
                "option 3": "...",
                "option 4": "..."
                },
                "correct_option": "option X"  // replace X with the correct option number
                }
                '''
            )
            response = llm.complete(prompt)
            raw_response = response.text.strip()  # Strip leading/trailing whitespace
            # print(f"Raw LLM response:\n{raw_response}")
            
            # Clean up the response
            try:
                # Attempt to load JSON directly
                question_json = json.loads(raw_response)
            except json.JSONDecodeError:
                # If direct loading fails, try to manually extract JSON part
                try:
                    json_start = raw_response.index('{')
                    json_end = raw_response.rindex('}') + 1
                    raw_response = raw_response[json_start:json_end]
                    # print(f"Cleaned LLM response:\n{raw_response}")
                    question_json = json.loads(raw_response)
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"Failed to parse JSON: {e}")
                    question_json = None
            
            if question_json is not None and validate_json_structure(question_json):
                questions.append(question_json)
                break
            else:
                print(f"Failed to parse JSON on attempt {attempt + 1}.")
        else:
            print("Failed to generate a valid question after 3 attempts.")

    return questions

def validate_json_structure(question_json):
    """Validate the structure of the JSON."""
    if "question" in question_json and "options" in question_json and "correct_option" in question_json:
        return True
    else:
        print("Invalid JSON format. Missing required keys.")
        return False

def display_questions(questions):
    """Display generated questions and collect user answers."""
    user_answers = {}
    for i, question in enumerate(questions):
        st.write(f"Question {i + 1}: {question['question']}")

        # Insert a hidden default choice
        options_with_default = ["(Select an option)"] + list(question['options'].values())

        user_answers[i] = st.radio(
            "Select your answer:",
            options=options_with_default,
            key=f"radio_{i}",
            index=0  # Default selection is the hidden choice
        )

        # Replace the selected dummy option with None
        if user_answers[i] == "(Select an option)":
            user_answers[i] = None

        st.write("")  # Add a blank line after each question
    return user_answers

def main():
    st.title("PDF to Quiz Generator")

    # Configure the number of questions
    num_questions = st.number_input("Number of questions:", min_value=1, max_value=100, value=10)

    # Step 1: Upload PDF and create index
    if "pdf_uploaded" not in st.session_state:
        uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

        if uploaded_file is not None:
            # Save the uploaded file temporarily
            temp_pdf_path = f"./temp_{str(uuid.uuid4())}.pdf"
            with open(temp_pdf_path, "wb") as temp_file:
                temp_file.write(uploaded_file.read())

            # Step 2: Create the index from the PDF and get the nodes
            vector_index, nodes = create_index_from_pdf(temp_pdf_path)

            # Store the necessary information in session state
            st.session_state["pdf_uploaded"] = True
            st.session_state["nodes"] = nodes
            st.session_state["vector_index"] = vector_index
            st.session_state["temp_pdf_path"] = temp_pdf_path

            st.success("PDF processed and index created successfully! Please proceed to generate the quiz.")
        else:
            st.stop()

    # Step 3: Generate questions from the nodes
    if "questions" not in st.session_state:
        st.session_state["questions"] = generate_questions_from_nodes(llm, st.session_state["nodes"], num_questions)

    # Step 4: Display the generated questions and collect answers
    user_answers = display_questions(st.session_state["questions"])

    # Final submit button
    if st.button("Submit Quiz"):
        if any(answer is None for answer in user_answers.values()):
            st.error("Please answer all questions before submitting.")
        else:
            # Calculate and display the result
            correct_answers = 0
            st.write("Quiz Results:")
            for i, question in enumerate(st.session_state["questions"]):
                # Find the selected key (A, B, C, D) from the options
                selected_option_key = next((k for k, v in question['options'].items() if v == user_answers[i]), None)
                correct_option_key = question['correct_option']

                if selected_option_key == correct_option_key:
                    correct_answers += 1
                    st.write(f"Question {i + 1}: Correct!")
                else:
                    st.write(f"Question {i + 1}: Incorrect! The correct answer was: {question['options'][correct_option_key]}")

            st.write(f"You answered {correct_answers} out of {num_questions} questions correctly!")

            # Clean up the temporary file
            os.remove(st.session_state["temp_pdf_path"])

            # Clear session state after submission
            st.session_state.clear()

if __name__ == "__main__":
    main()
