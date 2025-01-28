# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from transformers import pipeline
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud
from sqlalchemy import or_
import string
import io
import matplotlib.pyplot as plt
import nltk

# Download necessary NLTK data
nltk.download("punkt")
nltk.download("stopwords")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialize Flask-Migrate
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    avatar = db.Column(db.String(150), nullable=True)  # New column for profile picture
    is_admin = db.Column(db.Boolean, default=False)  # New field for admin role

# Analysis model for storing user analysis results
class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text_input = db.Column(db.Text, nullable=False)
    sentiment_label = db.Column(db.String(50), nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)
    keywords = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create the database
with app.app_context():
    db.create_all()

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize NLP pipelines
sentiment_analyzer = pipeline("sentiment-analysis")
summarizer = pipeline("summarization")

# Function to extract keywords
def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    stop_words.update(string.punctuation)
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    word_freq = Counter(filtered_tokens)
    return word_freq.most_common(5)

# Function to generate a word cloud
def generate_word_cloud(text):
    stop_words = set(stopwords.words("english"))
    wordcloud = WordCloud(stopwords=stop_words, background_color="white", width=800, height=400).generate(text)
    img_stream = io.BytesIO()
    plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(img_stream, format="png")
    plt.close()
    img_stream.seek(0)
    return img_stream

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register"))

        # Add user to the database
        hashed_password = generate_password_hash(password)  # Hash the password
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# User login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Authenticate user
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  # Check hashed password
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html")

# User logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Admin Dashboard Route
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied. Admins only!")
        return redirect(url_for("home"))

    # Query all users and analyses
    users = User.query.all()
    analyses = Analysis.query.all()

    return render_template("admin_dashboard.html", users=users, analyses=analyses)

# Routes to Manage Users and Analyses
@app.route("/delete_user", methods=["POST"])
@login_required
def delete_user():
    if not current_user.is_admin:
        flash("Access denied. Admins only!")
        return redirect(url_for("home"))

    user_id = request.form.get("user_id")
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!")
    else:
        flash("User not found!")

    return redirect(url_for("admin_dashboard"))

@app.route("/delete_analysis", methods=["POST"])
@login_required
def delete_analysis():
    if not current_user.is_admin:
        flash("Access denied. Admins only!")
        return redirect(url_for("home"))

    analysis_id = request.form.get("analysis_id")
    analysis = Analysis.query.get(analysis_id)

    if analysis:
        db.session.delete(analysis)
        db.session.commit()
        flash("Analysis deleted successfully!")
    else:
        flash("Analysis not found!")

    return redirect(url_for("admin_dashboard"))

# Profile route for updating user information
import os
from werkzeug.utils import secure_filename

# Configure the upload folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        avatar = request.files.get("avatar")  # Get the uploaded file

        # Validate input
        if not new_username or not new_password:
            flash("Both username and password are required.", "danger")
            return redirect(url_for("profile"))

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != current_user.id:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("profile"))

        # Update user details
        current_user.username = new_username
        current_user.password = generate_password_hash(new_password)

        # Handle avatar upload
        if avatar:
            filename = secure_filename(avatar.filename)
            avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            avatar.save(avatar_path)
            current_user.avatar = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=current_user)


# Define a route for the home page
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        text_input = request.form.get("text_input")
        if text_input:
            sentiment = sentiment_analyzer(text_input)
            sentiment_label = sentiment[0]["label"]
            sentiment_score = round(sentiment[0]["score"], 2)
            keywords = extract_keywords(text_input)
            summary = summarizer(text_input, max_length=50, min_length=10, do_sample=False)
            summary_text = summary[0]["summary_text"]

            # Save the analysis to the database
            analysis = Analysis(
                user_id=current_user.id,
                text_input=text_input,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score,
                keywords=str(keywords),
                summary=summary_text
            )
            db.session.add(analysis)
            db.session.commit()

            return render_template(
                "index.html",
                text_input=text_input,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score,
                keywords=keywords,
                summary_text=summary_text,
            )
    return render_template("index.html")

# Dashboard route for viewing saved analyses
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    query = request.args.get("query", "")
    sentiment_filter = request.args.get("sentiment", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    page = request.args.get("page", 1, type=int)  # Get the current page number

    analyses_query = Analysis.query.filter_by(user_id=current_user.id)

    if query:
        analyses_query = analyses_query.filter(
            or_(
                Analysis.text_input.ilike(f"%{query}%"),
                Analysis.summary.ilike(f"%{query}%")
            )
        )
    if sentiment_filter:
        analyses_query = analyses_query.filter(Analysis.sentiment_label == sentiment_filter)
    if start_date and end_date:
        analyses_query = analyses_query.filter(
            Analysis.timestamp.between(start_date, end_date)
        )

    # Paginate results (5 analyses per page)
    analyses = analyses_query.order_by(Analysis.timestamp.desc()).paginate(page=page, per_page=5)

    return render_template(
        "dashboard.html",
        analyses=analyses,
        query=query,
        sentiment_filter=sentiment_filter
    )

# Route for displaying the word cloud
@app.route("/wordcloud", methods=["POST"])
@login_required
def wordcloud():
    text_input = request.form.get("text_input")
    if text_input:
        img_stream = generate_word_cloud(text_input)
        return send_file(img_stream, mimetype="image/png")
    return "No text provided to generate a word cloud."

# Route for downloading results as a text file
@app.route("/download", methods=["POST"])
@login_required
def download():
    text_input = request.form.get("text_input")
    sentiment_label = request.form.get("sentiment_label")
    sentiment_score = request.form.get("sentiment_score")
    keywords = request.form.get("keywords")
    summary_text = request.form.get("summary_text")
    results_text = f"Input Text:\n{text_input}\n\n"
    results_text += f"Sentiment Analysis:\nSentiment: {sentiment_label}\nConfidence Score: {sentiment_score}\n\n"
    results_text += "Top Keywords:\n"
    for word, freq in eval(keywords):
        results_text += f"- {word}: {freq}\n"
    results_text += f"\nSummary:\n{summary_text}\n"
    output_file = "results.txt"
    with open(output_file, "w") as f:
        f.write(results_text)
    return send_file(output_file, as_attachment=True)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
