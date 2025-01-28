# NLP Text Analytics Tool

This project is an **NLP-based Text Analytics Tool** built using Python and Flask. It provides a user-friendly interface for analyzing text and extracting useful insights like sentiment analysis, keyword extraction, text summarization, and more. It is designed to showcase advanced natural language processing (NLP) capabilities and web application development.

---

## Features

- **User Authentication**: Secure user login and registration system with admin role support.
- **Sentiment Analysis**: Classify the sentiment of text input as positive, negative, or neutral with confidence scores.
- **Text Summarization**: Generate concise summaries of lengthy text inputs.
- **Keyword Extraction**: Extract key terms from the text for easy topic identification.
- **Word Cloud Generation**: Visualize frequently occurring words in a text.
- **User Dashboard**: View, search, and filter analysis history.
- **Admin Dashboard**: Manage users and their analysis data (admin-only).
- **Download Results**: Export analysis results as a text file.

---

## Technologies Used

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript (Jinja2 Templates)
- **NLP Models**: Hugging Face Transformers (Sentiment Analysis, Summarization)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Visualizations**: WordCloud, Matplotlib
- **Environment Management**: Virtual Environment (`venv`)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tonasoft/nlp-text-tool.git
   cd nlp-text-tool
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   flask run
   ```

5. Access the app in your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Usage

1. **Register** or **Log In** to access the app.
2. Enter text in the input field and analyze it.
3. View results like sentiment, keywords, summary, and a word cloud visualization.
4. Save analysis to the dashboard or download the results.

---

## Future Enhancements

- Deploy the app on a cloud platform (e.g., AWS, Heroku, or Azure).
- Add multilingual support for text analysis.
- Enable PDF and document file uploads for analysis.
- Integrate machine learning for improved sentiment analysis and text summarization.
- Enhance the UI/UX for a better user experience.

---

## Contributing

Contributions are welcome! Feel free to fork this repository and submit a pull request with your improvements or suggestions.

---

## License

This project is licensed under the [MIT License](LICENSE).

