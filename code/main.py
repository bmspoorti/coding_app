from flask import Flask, render_template, request, redirect, url_for
import psycopg
import json
from datetime import datetime

app = Flask(__name__)

def connect_to_database():
    try:
        conn = psycopg.connect(
            dbname="postgres",
            user="postgres",
            password="#Vandit3702",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg.Error as e:
        print("Error connecting to database:", e)
        return None
    
def fetch_candidate_questions(candidate_id):
    
    conn = connect_to_database()
    if conn:
        try:
            cur = conn.cursor()

            cur.execute("SELECT can_job FROM rec_candidates WHERE C_ID = %s", (candidate_id,))
            job_sel = cur.fetchone()[0] 

            cur.execute("SELECT question FROM ques_bank WHERE ques_tag = %s", (job_sel,))
            questions = cur.fetchall() 

            cur.close()
            conn.close()

            return questions
        
        except psycopg.Error as e:
            print("Error fetching candidate questions:", e)
            return []

def insert_answers(candidate_id, answers):
    conn = connect_to_database()
    if conn:
        try:
            cur = conn.cursor()

            query = "UPDATE rec_candidates SET "
            for question_key, answer in answers.items():
                question_number = int(question_key.split()[1])
                column_name = f"ques_{question_number}"
                query += f"{column_name} = %s, "

            query = query[:-2]  
            query += " WHERE c_id = %s"
            
            values = list(answers.values())
            values.append(candidate_id)

            cur.execute(query, tuple(values))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except psycopg.Error as e:
            print("Error inserting answers into database:", e)
            conn.rollback()
            conn.close()
            return False

def fetch_can_status(candidate_id):
    conn = connect_to_database()
    if conn:
        try:
            cur = conn.cursor()

            cur.execute("SELECT can_status FROM rec_candidates WHERE C_ID = %s", (candidate_id,))
            can_status = cur.fetchone()[0]  

            cur.close()
            conn.close()

            return can_status
        
        except psycopg.Error as e:
            print("Error fetching candidate status:", e)
            return []


@app.route('/')
def index():
    return render_template('index_ct_hhr.html')

@app.route('/test/<int:candidate_id>', methods=['GET', 'POST'])
def test(candidate_id):

    if request.method == 'POST':
        answers = {f"Question {i+1}": request.form.get(f'answer{i+1}') for i in range(len(request.form))}
        if insert_answers(candidate_id, answers):
            return redirect(url_for('status', candidate_id=candidate_id))
        else:
            return "Failed to submit answers. Please try again later."
    
    questions = fetch_candidate_questions(candidate_id)
    return render_template('test_ct_hhr.html', questions=questions)

@app.route('/status/<int:candidate_id>')
def status(candidate_id):
    pv = fetch_can_status(candidate_id)
    if pv == 2:
        progress_value = 37
    elif pv == 3:
        progress_value = 67
    elif pv == 4:
        progress_value = 100
    else:
        progress_value = 0

    return render_template('status_ct_hhr.html',progress_value=progress_value)

if __name__ == '__main__':
    app.run(debug=True,port=8005)
