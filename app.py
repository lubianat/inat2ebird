import requests
from flask import Flask, request, render_template_string, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename
import os
from io import StringIO
import csv
from user2ebird import *
from observation2ebird import *

from flask import send_from_directory

# Flask app initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Necessary for flash messages to work

# Set the directory for uploaded files (adjust as needed)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        user_id = request.form["user_id"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            save_all_observations_from_user(
                user_id,
                only_new_taxa=True,
                path_to_life_list=f"{UPLOAD_FOLDER}/ebird_world_life_list.csv",
                base_dir=UPLOAD_FOLDER,
            )
    return render_template_string(
        """
        <h1>iNaturalist to eBird Importer</h1>
        <form method="post" enctype="multipart/form-data">
            <label for="user_id">Enter the iNaturalist user ID:</label>
            <input type="text" id="user_id" name="user_id" required>
            <label for="file">Upload your eBird life list (CSV):</label>
            <input type="file" id="file" name="file" accept=".csv" required>
            <input type="submit" value="Submit">
        </form>
        <p>Make sure you download your life list from <a href="https://ebird.org/lifelist?time=life&r=world">here</a> as 'ebird_world_life_list.csv'</p>
        <p>Also make sure you add to observation2ebird your valid eBird API key (<a href="https://ebird.org/api/keygen">get it here</a>).</p>
        <p>After downloading your new entries, upload them in the eBird record format at <a href="https://ebird.org/import/upload.form?theme=ebird">this link</a>.</p>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul>
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
    """
    )


@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )


@app.route("/submit", methods=["POST"])
def submit():
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["file"]
    user_id = request.form["user_id"]
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        try:
            save_all_observations_from_user(
                user_id, filepath, only_new_taxa=True, base_dir=UPLOAD_FOLDER
            )
            output_filename = f"all_bird_entries_{user_id}.csv"
            flash(f"Entries saved to {output_filename}")
            flash("Click the link below to download your entries.")
            return render_template_string(
                """
                <h1>Success!</h1>
                <p>Your observations have been saved. Click below to download the CSV file.</p>
                <a href="{{ url_for('download_file', filename=output_filename) }}">Download CSV</a>
                <a href="/">Submit another ID</a>
                """,
                output_filename=output_filename,
            )
        except Exception as e:
            flash(f"An error occurred: {e}")
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
