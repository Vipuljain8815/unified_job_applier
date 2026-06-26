from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

PATH = 'all excels/'
##> ------ Karthik Sarode : karthik.sarode23@gmail.com - UI for excel files ------
@app.route('/')
def home():
    """Displays the home page of the application."""
    return render_template('index.html')

@app.route('/applied-jobs', methods=['GET'])
def get_applied_jobs():
    '''
    Retrieves a list of applied jobs from the applications history CSV file.
    
    Returns a JSON response containing a list of jobs, each with details such as 
    Job ID, Title, Company, HR Name, HR Link, Job Link, External Job link, and Date Applied.
    
    If the CSV file is not found, returns a 404 error with a relevant message.
    If any other exception occurs, returns a 500 error with the exception message.
    '''

    try:
        jobs = []
        csvPath = os.path.join(PATH, 'all_applied_applications_history.csv')
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs.append({
                    'Job_ID': row.get('Job ID', 'N/A'),
                    'Title': row.get('Title', 'N/A'),
                    'Company': row.get('Company', 'N/A'),
                    'HR_Name': row.get('HR Name', 'N/A'),
                    'HR_Link': row.get('HR Link', 'N/A'),
                    'Job_Link': row.get('Job Link', 'N/A'),
                    'External_Job_link': row.get('External Job link', 'N/A'),
                    'Date_Applied': row.get('Date Applied', 'N/A')
                })
        # Limit to the last 1000 jobs to prevent frontend lag
        return jsonify(jobs[-1000:])
    except FileNotFoundError:
        return jsonify({"error": "No applications history found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/applied-jobs/<job_id>', methods=['PUT'])
def update_applied_date(job_id):
    """
    Updates the 'Date Applied' field of a job in the applications history CSV file.

    Args:
        job_id (str): The Job ID of the job to be updated.

    Returns:
        A JSON response with a message indicating success or failure of the update
        operation. If the job is not found, returns a 404 error with a relevant
        message. If any other exception occurs, returns a 500 error with the
        exception message.
    """
    try:
        data = []
        csvPath = os.path.join(PATH, 'all_applied_applications_history.csv')
        
        if not os.path.exists(csvPath):
            return jsonify({"error": f"CSV file not found at {csvPath}"}), 404
            
        # Read current CSV content
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldNames = reader.fieldnames
            found = False
            for row in reader:
                if row['Job ID'] == job_id:
                    row['Date Applied'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    found = True
                data.append(row)
        
        if not found:
            return jsonify({"error": f"Job ID {job_id} not found"}), 404

        with open(csvPath, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(data)
        
        return jsonify({"message": "Date Applied updated successfully"}), 200
    except Exception as e:
        print(f"Error updating applied date: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route('/sent-emails', methods=['GET'])
def get_sent_emails():
    '''
    Retrieves a list of sent emails from the email history CSV file.
    '''
    try:
        emails = []
        csvPath = os.path.join(PATH, 'all_emails_sent_history.csv')
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                emails.append({
                    'Date': row.get('Date', 'N/A'),
                    'Author': row.get('Author', 'N/A'),
                    'Email_Found': row.get('Email Found', 'N/A'),
                    'Subject_Sent': row.get('Subject Sent', 'N/A'),
                    'Comment_Added': row.get('Comment Added', 'N/A'),
                    'Status': row.get('Status', 'N/A')
                })
        return jsonify(emails[-1000:])
    except FileNotFoundError:
        return jsonify({"error": "No email history found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

##<