
# PDF to Quiz Generator

This project is a Streamlit application that allows users to upload a PDF, extract its text, and automatically generate a quiz with multiple-choice questions based on the document content. The application leverages OpenAI's GPT-4 to create questions and validate the answers. The quiz is presented in a user-friendly interface where participants can select their answers and view the results immediately.

## Features

- **PDF Upload & Text Extraction:** Upload a PDF document, and the app extracts its text for further processing.
- **Question Generation:** Automatically generate multiple-choice questions from the extracted text using OpenAI's GPT-4 API.
- **Interactive Quiz:** Present the questions in an interactive format using Streamlit, allowing users to submit their answers and view results.
- **Dockerized Setup:** Easily deploy and run the application using Docker for a consistent environment.

- ![Screenshot 2024-08-25 131854](https://github.com/user-attachments/assets/fe9787bf-c67b-4c55-a6e9-0c20dcdf8ff3)
- ![Screenshot 2024-08-25 131928](https://github.com/user-attachments/assets/f66203ce-9c8f-4c26-8e58-92a5288eec81)
- ![Screenshot 2024-08-25 131944](https://github.com/user-attachments/assets/3cbfe6a4-05ce-4d5b-aed9-059f15d8760a)




## Prerequisites

- Python 3.10 or higher
- Docker (for containerized setup)
- OpenAI API Key

## Installation

### Local Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/nikhildutta333/random-quiz-generator.git
    cd random-quiz-generator
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your OpenAI API Key:**
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    ```

5. **Run the application:**
    ```bash
    streamlit run app.py
    ```

### Docker Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/nikhildutta333/random-quiz-generator.git
    cd random-quiz-generator
    ```

2. **Build the Docker image:**
    ```bash
    docker build -t random-quiz-generator .
    ```

3. **Run the Docker container:**
    ```bash
    docker run -p 8501:8501 -e OPENAI_API_KEY="your-openai-api-key" random-quiz-generator
    ```

4. **Access the application:**
   Open your web browser and navigate to `http://localhost:8501`.

## Usage

1. **Upload a PDF File:**
   - Drag and drop your PDF file into the uploader on the application interface.

2. **Generate Quiz:**
   - Specify the number of questions you want to generate and let the application process the text and create the quiz.

3. **Take the Quiz:**
   - Answer the multiple-choice questions generated from the document's content.

4. **Submit and View Results:**
   - After completing the quiz, submit your answers to see your score and the correct answers.

## File Structure

```
random-quiz-generator/
│
├── app.py                  # Main application script
├── Dockerfile              # Dockerfile for containerized deployment
├── requirements.txt        # List of Python dependencies
├── README.md               # Project documentation
└── storage/                # Directory to store the vector index (created at runtime)
```

## Contributing

Contributions are welcome! Please fork this repository, make your changes, and submit a pull request for review.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OpenAI](https://www.openai.com/) for providing the GPT-4 API.
- [Streamlit](https://streamlit.io/) for the interactive app framework.
- [PyPDF2](https://pypi.org/project/PyPDF2/) for PDF text extraction.
