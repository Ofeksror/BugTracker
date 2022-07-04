from re import A
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import datetime

from helpers import login_required

app = Flask(__name__)
db = sqlite3.connect('bugger.db', check_same_thread=False)
# db.row_factory = sqlite3.Row
cursor = db.cursor()


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.run(debug=True)
Session(app)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    
    if request.method == "POST":
        email_input = request.form.get("email")
        valid_pass = cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email_input,)).fetchall()
        
        if len(valid_pass) != 1:
            error = "Invalid email/password"
            return render_template("login.html", error=error)
        elif not check_password_hash(valid_pass[0][0], request.form.get("password")):
            error = "Invalid email/password"
            return render_template("login.html", error=error)
        
        session["user_id"] = cursor.execute("SELECT id FROM users WHERE email = ?", (email_input,)).fetchall()[0][0]
        session["role"] = cursor.execute("SELECT role FROM users WHERE email = ?", (email_input,)).fetchall()[0][0]
        session["company"] = cursor.execute("SELECT company_id FROM users WHERE email = ?", (email_input,)).fetchall()[0][0]
        if session["company"] == 0:
            session["company"] = None
        
        flash("Logged in successfully!")
        return redirect("/")
    else:
       return render_template("login.html")


@app.route("/logout")
def logout():
    """ Logs user out """
    
    session.clear()
    
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """ REGISTERS USERS TO THE SYSTEM """
        
        email = request.form.get("email")
        password = request.form.get("password")
        c_password = request.form.get("c_password")
        slack = request.form.get("slack")
        
        # Check validity
        if len(cursor.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchall()) != 0:
            error = "Email already exists"
            return render_template("register.html", error=error)
        elif c_password != password:
            error = "Passwords don't match"
            return render_template("register.html", error=error)
        
        
        """ INDEED NEW USER """
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        
        # Hash password
        password = generate_password_hash(password)
    
        if slack:
            cursor.execute("INSERT INTO users (first_name, last_name, email, password_hash, slack) VALUES (?, ?, ?, ?, ?)", (first_name, last_name, email, password, slack,))
            db.commit()
        else:
            cursor.execute("INSERT INTO users (first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?)", (first_name, last_name, email, password,))
            db.commit()

        session["user_id"] = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchall()[0][0]
        session["role"] = None
        session["company"] = None
        
        flash_message = "Account created successfully! Welcome, " + first_name
        flash(flash_message)
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/createCompany", methods=["GET", "POST"])
def createCompany():
    if request.method == "POST":
        cName = request.form.get("companyName")
        
        # print(cursor.execute("SELECT name FROM companies WHERE name = ?", (cName,)).fetchall())
        # print(len(cursor.execute("SELECT name FROM companies WHERE name = ?", (cName,)).fetchall()))
        # return render_template("newCompany.html")
        
        # Check if name already exists
        if len(cursor.execute("SELECT name FROM companies WHERE name = ?", (cName,)).fetchall()) != 0:
            return render_template("newCompany.html", error="Company already exists")
        
        # Creates new company        
        cursor.execute("INSERT INTO companies (name) VALUES (?)", (cName,))
        
        # Sets user as admin of created company
        cId = cursor.execute("SELECT id FROM companies WHERE name = ?", (cName,)).fetchall()[0][0]
        cursor.execute("UPDATE users SET role='admin', company_id=? WHERE id = ?", (cId, session["user_id"],))
        session["role"] = 'admin'
        db.commit()
        
        flash(f"Welcome, you are now the admin of {cName}")
        return redirect("/")
    else:
        if session["role"] != None:
            return redirect('/')
        if session["company"] != None:
            return redirect("/")
        
        return render_template("newCompany.html")


@app.route("/")
@login_required
def homepage():    
    if session["role"] == "dev" or session["role"] == "tester":
        tickets = cursor.execute("SELECT * FROM tickets WHERE accepted = 1 AND id IN (SELECT ticket_id FROM assignedtickets WHERE dev_id = ?)", (session['user_id'],)) # .fetchall()[0]

        fTickets = []
        for ticket in tickets:
            first, last = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (ticket[8],)).fetchall()[0]
            fTickets.append({
                "id": ticket[0],
                "title": ticket[1],
                "description": ticket[2],
                "status": ticket[3],
                "priority TEXT": ticket[4],
                "type TEXT": ticket[5],
                "deadline": ticket[6],
                "time_estimate": ticket[7],
                "author": f"{first} {last}",
                "date_added": ticket[9],
                "project": ticket[10]
            })

        return render_template("dashDev.html", Tickets1=fTickets)
    elif session["role"] == "manager":
        return render_template("dashManager.html")
    elif session["role"] == "admin":
        return render_template("dashAdmin.html")
    else:
        return render_template("newuser.html")


@app.route("/test/newticket", methods=["GET", "POST"])
@login_required
def testNewTicket():
    if request.method == "POST":
        Title = request.form.get("title")
        Description = request.form.get("description")
        
        Status = request.form.get("status")
        Priority = request.form.get("priority")
        Type = request.form.get("type")
        
        Deadline = request.form.get('deadline')
        Estimate = request.form.get("time_estimate")
        
        Author = session["user_id"]
        
        DateAdded = datetime.datetime.now()
        
        Project = request.form.get("project")
        
        cursor.execute('INSERT INTO tickets (title, description, status, priority, type, deadline, time_estimate, author, date_added, project) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (Title, Description, Status, Priority, Type, Deadline, Estimate, Author, DateAdded, Project))
        # ticketID = cursor.execute('SELECT id FROM tickets WHERE date_added = ?', (DateAdded,)).fetchall()[0][0]
        
        db.commit()
        flash("Ticket created successfuly")
        return redirect('/test/newticket')
    else:
        # TODO Add condition -> only projects that aren't closed
        
        if session['role'] == 'admin' or 'manager':
            # Show all company projects
            
            company_id = cursor.execute('SELECT company_id FROM users WHERE id = ?', (session['user_id'],)).fetchall()[0][0]
            projects_raw = cursor.execute('SELECT id, title FROM projects WHERE company = ?', (company_id,)).fetchall()
            
            projects = []
            for project in projects_raw:
                projects.append({
                    'id': project[0],
                    'title': project[1]
                })
            
            return render_template("testNewTicket.html", Projects=projects)
            
        elif session['role'] == 'dev' or 'tester':
            # Show only assigned projects

            project_ids = cursor.execute('SELECT project_id FROM assignedprojects WHERE dev_id = ?', (session['user_id'],)).fetchall()
            projects_raw = cursor.execute('SELECT id, title FROM projects WHERE id IN ?', (project_ids,)).fetchall()
            
            projects = []
            for project in projects_raw:
                projects.append({
                    'id': project[0],
                    'title': project[1]
                })
            
            return render_template("testNewTicket.html", Projects=projects)
            
        else:
            # User has no role
            return redirect('/')


@app.route("/test/newProject", methods=["GET", "POST"])
@login_required
def newProject():
    if request.method == "POST":
        title = request.form.get("title")
        status = request.form.get("status")
        
        if not status:
            status = 'Open'

        # companyId = cursor.execute('SELECT company_id FROM users WHERE id=?', (session['user_id'],)).fetchall()[0][0]
        companyId = session["company"]
        
        cursor.execute('INSERT INTO projects (company ,title, status) VALUES (?, ?, ?)', (companyId, title, status,))
        db.commit()
        
        flash("Project created!")
        return redirect("/test/newProject")
    else:
        if session['role'] != 'admin' or 'manager':
            return render_template('newProject.html')


@app.route("/test/team", methods = ["GET", "POST"])
@login_required
def userManagement():
    if request.method == 'POST':
        flash('POST')
        return redirect('/test/team')
    else:
        raw_users = cursor.execute("SELECT * FROM users WHERE company_id = ?", (session["company"],)).fetchall()
        print(raw_users)
        
        users = []
        for user in raw_users:
            users.append({
                "id": user[0],
                "first": user[1],
                "last": user[2],
                "email": user[3],
                "role": user[6]
             })
        
        return render_template('users.html', Users=users)


@app.route("/inviteUser", methods=["POST"])
def inviteUser():
    email = request.form.get('email')

    # Check if user exists in system
    user_id = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchall()
    if len(user_id) != 1:
        flash("User doesn't exist.")
        return redirect("/test/team")
    
    # Gets input
    user_id = user_id[0][0]
    role = request.form.get('role')
    company_id = cursor.execute("SELECT company_id FROM users WHERE id = ?", (session['user_id'],)).fetchall()[0][0]
    
    # Checks if user is already in a company
    if cursor.execute("SELECT company_id FROM users WHERE id = ?", (user_id,)).fetchall()[0][0]:
        flash("User is already assigned to a company")
        return redirect("/test/team")
    
    # Checks if user is already a member of the company
    if company_id == cursor.execute("SELECT company_id FROM users WHERE id = ?", (user_id,)).fetchall()[0][0]:
        flash("User is already assigned to a company")
        return redirect("/test/team")
    
    # Assigns user to company
    cursor.execute("UPDATE users SET role=?, company_id=? WHERE id = ?", (role, company_id, user_id))

    flash("User is now a member of your company")
    return redirect("/test/team")

    
db.commit()