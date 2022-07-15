from flask import Flask, render_template, request, redirect, session, flash, abort
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import datetime

# import handlers
from helpers import login_required, queryToDate, projectsPercentage


app = Flask(__name__)
db = sqlite3.connect('bugger.db', check_same_thread=False)
# db.row_factory = sqlite3.Row
cursor = db.cursor()


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# app.run(debug=True)
Session(app)



@app.errorhandler(404)
def error_404(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(e):
    return render_template('errors/500.html'), 500


@app.errorhandler(405)
def error_405(e):
    return render_template('errors/405.html'), 405


@app.route("/account/login", methods=["GET", "POST"]) #/login
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


@app.route("/account/demo")
def demoSelect():
    if 'user_id' in session:
        abort(404)
    return render_template("demoselect.html")


@app.route("/account/demo/admin")
def demoAdmin():
    if 'user_id' in session:
        abort(403)
        
    session['user_id'] = 16
    session['company'] = 3
    session['role'] = 'admin'
    return redirect('/')


@app.route("/account/demo/manager")
def demoManager():
    if 'user_id' in session:
        abort(403)
        
    session['user_id'] = 20
    session['company'] = 3
    session['role'] = 'manager'
    return redirect('/')


@app.route("/account/demo/developer")
def demoDeveloper():
    if 'user_id' in session:
        abort(403)
    
    session['user_id'] = 29
    session['company'] = 3
    session['role'] = 'dev'
    return redirect('/')


@app.route("/account/password", methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "POST":
        oldPass = request.form.get('oldpassword')
        actPass = cursor.execute("SELECT password_hash FROM users WHERE id = ?", (session['user_id'],)).fetchall()[0][0]
        if not check_password_hash(actPass, oldPass):
            flash("Old password is invalid")
            return redirect('/account/password')
        
        newPass = request.form.get('newpassword')
        
        if oldPass == newPass:
            flash("New password can't match old password")
            return redirect('/account/password')
        
        conPass = request.form.get('conpassword')
        
        if newPass != conPass:
            flash("Confirmation doesn't match new password")
            return redirect('/account/password')
        
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(newPass), session['user_id'],))
        
        flash("Successfuly changed password!")
        return redirect('/account/password')
    else:
        return render_template('changePassword.html')


@app.route("/account/logout") #/logout
def logout():
    """ Logs user out """
    
    session.clear()
    
    return redirect("/")


@app.route("/account/register", methods=["GET", "POST"]) #/register
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
        if 'user_id' in session:
            abort(404)
        return render_template("register.html")


@app.route("/new/company", methods=["GET", "POST"]) #createCompany
def createCompany():
    if request.method == "POST":
        cName = request.form.get("companyName")
        
        # Check if name already exists
        if len(cursor.execute("SELECT name FROM companies WHERE name = ?", (cName,)).fetchall()) != 0:
            return render_template("newCompany.html", error="Company already exists")
        
        # Creates new company        
        cursor.execute("INSERT INTO companies (name) VALUES (?)", (cName,))
        
        # Sets user as admin of created company
        cId = cursor.execute("SELECT id FROM companies WHERE name = ?", (cName,)).fetchall()[0][0]
        cursor.execute("UPDATE users SET role='admin', company_id=? WHERE id = ?", (cId, session["user_id"],))
        session['role'] = 'admin'
        session['company'] = cursor.lastrowid
        db.commit()
        
        flash(f"Welcome, you are now the admin of {cName}")
        return redirect("/")
    else:
        if session['role'] != None:
            abort(404)
        if session['company'] != None:
            abort(404)
        
        return render_template("newCompany.html")


@app.route("/")
@login_required
def dashboard():
    if session["role"] == "dev" or session["role"] == "tester":
        # Get all tickets
        tickets = cursor.execute("SELECT * FROM tickets WHERE accepted = 1 AND id IN (SELECT ticket_id FROM assignedtickets WHERE dev_id = ?)", (session['user_id'],)).fetchall() # .fetchall()[0]

        # Setup for Kanban Board
        openTickets = []
        inProgressTickets = []
        resolvedTickets = []
         
        newTickets = []
                
        for ticket in tickets:
            # Gets each ticket's properties
            firstName, lastName = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (ticket[8],)).fetchall()[0]
            properties = {
                "id": ticket[0],
                "title": ticket[1],
                "description": ticket[2],
                "status": ticket[3],
                "priority": ticket[4],
                "type": ticket[5],
                "deadline": ticket[6],
                "time_estimate": ticket[7],
                "author": f"{firstName} {lastName}",
                "date_added": ticket[9],
                "project": ticket[10],
                "projectName": cursor.execute("SELECT title FROM projects WHERE id = ?", (ticket[10],)).fetchall()[0][0]
            }
            
            # Assigns tickets to list grouped by status
            # Also adds percentage key based on status
            if properties['status'] == 'Open':
                openTickets.append(properties)
                properties['percentage'] = 0
            elif properties['status'] == 'In Progress':
                inProgressTickets.append(properties)        
                properties['percentage'] = 50
            elif properties['status'] == 'Resolved':
                resolvedTickets.append(properties)
                properties['percentage'] = 100
            
            newTickets.append(properties)
        
        projects = []
        sProjects = cursor.execute("SELECT id, title FROM projects WHERE company = ?", (session['company'],)).fetchall()
        for p in sProjects:
            projects.append({
                "ID": p[0],
                "Title": p[1]
            })

        # Renders HTML with setup
        return render_template("dashDev.html", Tickets=newTickets, OpenTickets=openTickets, InProgressTickets=inProgressTickets, ResolvedTickets=resolvedTickets, Projects=projects, GanttHeight=30*len(newTickets))
    elif session["role"] == "manager":
        # Get a list of projects assigned to manager
        projectsAssigned = cursor.execute("SELECT project_id FROM assignedprojects WHERE manager_id = ?", (session['user_id'],)).fetchall()
        
        openTickets = []
        inprogressTickets = []
        resolvedTickets = []
        
        tickets = []
        
        Projects = []
        
        for pID in projectsAssigned:
            projectTitle = cursor.execute("SELECT title FROM projects WHERE id = ?", (pID[0],)).fetchall()[0][0]
            
            pTickets = cursor.execute("SELECT * FROM tickets WHERE project = ?", (pID[0],)).fetchall()

            # Initial variables to calculate each project's completion percentage
            percentage = 0
            count = 0
            
            for ticket in pTickets:      
                firstName, lastName = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (ticket[8],)).fetchall()[0]
                t = {
                    "id": ticket[0],
                    "title": ticket[1],
                    "description": ticket[2],
                    "status": ticket[3],
                    "priority": ticket[4],
                    "type": ticket[5],
                    "deadline": ticket[6],
                    "time_estimate": ticket[7],
                    "author": f"{firstName} {lastName}",
                    "date_added": ticket[9],
                    "project": ticket[10],
                    "projectName": projectTitle
                }
                
                count += 1
                
                if t['status'] == 'In Progress':
                    percentage += 50
                    inprogressTickets.append(t)
                elif t['status'] == 'Resolved':
                    percentage += 100
                    resolvedTickets.append(t)
                else:
                    openTickets.append(t)
                
                tickets.append(t)
                    
            if count == 0:
                percentDone = 0
            else:
                percentDone = percentage / count
                
            Projects.append({
                'ID': pID[0],
                'Title': projectTitle,
                'Status': cursor.execute("SELECT status FROM projects WHERE id = ?", (pID[0],)).fetchall()[0][0],
                'Done': percentDone
            })
        
        return render_template("dashManager.html", Tickets=tickets, OpenTickets=openTickets, InProgressTickets=inprogressTickets, ResolvedTickets=resolvedTickets, Projects=Projects, GanttHeight=30*len(tickets))
    elif session["role"] == "admin":
        companyProjects = cursor.execute("SELECT id, title, status FROM projects WHERE company = ?", (session['company'],)).fetchall()
        projects = []
        openProjects = []
        inProgressProjects = []
        closedProjects = []
        
        # print(companyProjects)
        
        for project in companyProjects:
            # Get all tickets of project to a list
            pTickets = cursor.execute("SELECT date_added, deadline FROM tickets WHERE date_added IS NOT NULL AND date_added IS NOT '' AND deadline IS NOT '' AND deadline IS NOT NULL AND accepted = 1 AND project = ?", (project[0],)).fetchall()
            
            minDate = datetime.date.today()
            maxDate = datetime.date.today()
                        
            if pTickets:
                minDate = queryToDate(pTickets[0][0])
                maxDate = queryToDate(pTickets[0][1])
                
                for ticket in pTickets:
                    ticketStart = queryToDate(ticket[0])
                    ticketEnd = queryToDate(ticket[1])
                    
                    if ticketStart < minDate:
                        minDate = ticketStart
                    
                    if ticketEnd > ticketEnd:
                        maxDate = ticketEnd
                
            if project[2] == 'Closed':
                percentage = 100
                closedProjects.append({
                    'ID': project[0],
                    'Title': project[1],
                    'Start': minDate,
                    'End': maxDate
                })
            elif project[2] == 'In Progress':
                percentage = 50
                inProgressProjects.append({
                    'ID': project[0],
                    'Title': project[1],
                    'Start': minDate,
                    'End': maxDate
                })
            else:
                percentage = 0
                openProjects.append({
                    'ID': project[0],
                    'Title': project[1],
                    'Start': minDate,
                    'End': maxDate
                })
            
            projects.append({
                'ID': project[0],
                'Title': project[1],
                'Status': project[2],
                'Percentage': percentage,
                'Start': minDate,
                'End': maxDate
            })
            
        # Get an approximate start and end date for each project, displayed as a gantt chart
            # Find the earliest starting date out of each project's tickets
            # Find the latest deadline out of each project's tickets
        # projects = {'projectID': { 'id': id, 'start-date': date, 'end-date', date}}
        
        # print(projects)
        
        newProjects = projectsPercentage(session['company'])
        
        return render_template("dashAdmin.html", Projects=projects, NewProjects=newProjects, OpenProjects=openProjects, InProgressProjects=inProgressProjects, ClosedProjects=closedProjects, GanttHeight=30*len(projects))
    else:
        return redirect('/account/wait')


@app.route('/account/wait') #/wait
def wait():
    if not session['user_id']:
        return redirect('/account/login')
    testCompany = cursor.execute('SELECT company_id FROM users WHERE id = ?', (session['user_id'],)).fetchall()[0][0]
    if testCompany:
        session['role'] = cursor.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchall()[0][0]
        session['company'] = testCompany
        return redirect('/')
    else:
        return render_template("newuser.html")


@app.route("/new/ticket", methods=["POST"])
@login_required
def newTicket():
    Title = request.form.get("title")
    Description = request.form.get("description")
    
    Status = request.form.get("status")
    Priority = request.form.get("priority")
    Type = request.form.get("type")
    
    Deadline = request.form.get('deadline')
    
    Estimate = request.form.get("time_estimate")
    
    Author = session["user_id"]
    
    authorRole = session['role']
    if authorRole == 'dev':
        Accepted = 0
    elif authorRole == 'tester':
        Accepted = 0
    elif authorRole == 'manager':
        Accepted = 1
    elif authorRole == 'admin':
        Accepted = 1
    
    DateAdded = datetime.date.today()
    
    Project = request.form.get("projects")
    
    cursor.execute('INSERT INTO tickets (title, description, status, priority, type, deadline, time_estimate, author, date_added, project, accepted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (Title, Description, Status, Priority, Type, Deadline, Estimate, Author, DateAdded, Project, Accepted))
    
    db.commit()
    flash("Ticket reported successfuly.")
    if authorRole != 'admin':
        return redirect('/')
    return redirect('/control/tickets')


@app.route("/control/team", methods = ["GET", "POST"]) #/test/team
@login_required
def userManagement():
    if request.method == 'POST':
        email = request.form.get('changeRoleEmail')
        role = request.form.get('user-EditRole')
        cursor.execute("UPDATE users SET role = ? WHERE email = ?", (role, email,))
        
        flash("Role was updated for user")
        return redirect('/control/team')
    else:
        # Only allow access to admin
        if session['role'] != 'admin':
            return redirect('/')
        
        # Selects all users who work at the company
        raw_users = cursor.execute("SELECT * FROM users WHERE company_id = ?", (session['company'],)).fetchall()

        users = []
        for raw_user in raw_users:
            users.append({
                "id": raw_user[0],
                "first": raw_user[1],
                "last": raw_user[2],
                "email": raw_user[3],
                "slack": raw_user[5],
                "role": raw_user[6]
             })

        return render_template('users.html', Users=users)


@app.route("/control/new/member", methods=["POST"]) #/inviteUser
def inviteUser():
    email = request.form.get('email')

    # Check if user exists in system
    user_id = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchall()
    if len(user_id) != 1:
        flash("User doesn't exist.")
        return redirect("/control/team")
    
    # Gets input
    user_id = user_id[0][0]
    role = request.form.get('role')
    company_id = cursor.execute("SELECT company_id FROM users WHERE id = ?", (session['user_id'],)).fetchall()[0][0]
    
    # Checks if user is already a member of the company
    if company_id == cursor.execute("SELECT company_id FROM users WHERE id = ?", (user_id,)).fetchall()[0][0]:
        flash("User is already a member of the company")
        return redirect("/control/team")
    
    # Checks if user is already in a company
    if cursor.execute("SELECT company_id FROM users WHERE id = ?", (user_id,)).fetchall()[0][0] != None:
        flash("User is already assigned to a company")
        return redirect("/control/team")
    
    # Assigns user to company
    cursor.execute("UPDATE users SET role=?, company_id=? WHERE id = ?", (role, company_id, user_id))
    db.commit()
    
    flash("User is now a member of your company")
    return redirect("/control/team")


@app.route("/control/remove/member", methods=["POST"]) #/test/removeUser
def removeUser():
    email = request.form.get('userEmailDelete')
    
    # Ignores requests to remove an admin user from company
    role = cursor.execute("SELECT role FROM users WHERE email = ?", (email,)).fetchall()[0][0]
    if role == "admin":
        flash("Cannot remove an admin user from company")
        return redirect("/control/team")
    
    cursor.execute("UPDATE users SET company_id=?, role=? WHERE email=?", (None, None, email,))
    db.commit()
    
    flash("User has been removed from company")
    return redirect("/control/team")


@app.route("/control/remove/ticket", methods=["POST"]) #/deleteTicket
def deleteTicket():
    ticketID = request.form.get("deleteTicketID")
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticketID,))
    db.commit()
    
    if session['role'] == 'admin':
        return redirect("/control/tickets")
    elif session['role'] == 'manager':
        return redirect('/')


@app.route("/control/tickets", methods=["GET", "POST"]) #/test/tickets
@login_required
def testTicketManagement():
    if request.method == 'POST':
        ticket_id = request.form.get("ticket-ID")
        title = request.form.get("ticket-Title")
        description = request.form.get("ticket-Description")
        t_type = request.form.get("ticket-Type")
        status = request.form.get("ticket-Status")
        priority = request.form.get("ticket-Priority")
        deadline = request.form.get("ticket-Deadline")
        time_estimate = request.form.get("ticket-TimeEstimate")
        project = request.form.get("ticket-Projects")
        
        cursor.execute("UPDATE tickets SET title=?, description=?, status=?, priority=?, type=?, deadline=?, time_estimate=?, project=?, accepted = 1 WHERE id = ?", (title, description, status, priority, t_type, deadline, time_estimate, project, ticket_id,))
        
        assigned = request.form.getlist('ticket-Assign')
        cursor.execute("DELETE FROM assignedtickets WHERE ticket_id = ?", (ticket_id,))
        for member in assigned:
            flash(member)
            cursor.execute("INSERT INTO assignedtickets (ticket_id, dev_id) VALUES (?, ?)", (ticket_id, member,))
        
        db.commit()
        
        flash("Ticket updated successfully")
        return redirect("/control/tickets")
    else:
        if session['role'] != 'admin':
            return redirect('/')
        
        raw_tickets = cursor.execute("SELECT * FROM tickets WHERE project IN (SELECT id FROM projects WHERE company = ?)", (session['company'],)).fetchall()
        
        unaccepted_tickets = []
        accepted_tickets = []
        
        for raw_ticket in raw_tickets:
            # print(raw_ticket)
            first, last = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (raw_ticket[8],)).fetchall()[0]
            author = first + " " + last
            properties = {
                "id": raw_ticket[0],
                "title": raw_ticket[1],
                "description": raw_ticket[2],
                "status": raw_ticket[3],
                "priority": raw_ticket[4],
                "type": raw_ticket[5],
                "deadline": raw_ticket[6],
                "time_estimate": raw_ticket[7],
                "author": author,
                "date_added": raw_ticket[9],
                "project": cursor.execute("SELECT title FROM projects WHERE id = ?", (raw_ticket[10],)).fetchall()[0][0],
                "project_id": raw_ticket[10],
            }
            
            if raw_ticket[11] == 0 or raw_ticket[11] == None:
                unaccepted_tickets.append(properties)
            elif raw_ticket[11] == 1:
                accepted_tickets.append(properties)
        
        raw_projects = cursor.execute('SELECT id, title FROM projects WHERE company = ?', (session['company'],)).fetchall()
        projects = []
        for i in raw_projects:
            projects.append({
                "id": i[0],
                "title": i[1]
            })
            
        raw_members = cursor.execute('SELECT id, first_name, last_name, role FROM users WHERE company_id = ?', (session['company'],)).fetchall()
        members = []
        for i in raw_members:
            members.append({
                "id": i[0],
                "name": i[1] + " " + i[2],
                "role": i[3].title()
            })
        
        return render_template("tickets.html", UnacceptedTickets=unaccepted_tickets, AcceptedTickets=accepted_tickets, Projects=projects, Members=members)
    

@app.route("/control/projects", methods=["GET", "POST"])
@login_required
def displayProjects():
    if request.method == "POST":
        title = request.form.get("title")
        status = request.form.get("status")
        
        if not status:
            status = 'Open'

        cursor.execute('INSERT INTO projects (company ,title, status) VALUES (?, ?, ?)', (session['company'], title, status,))
        projectID = cursor.lastrowid
        
        newAssign = request.form.getlist("project-Assign")
        for member in newAssign:
            cursor.execute("INSERT INTO assignedprojects (project_id, manager_id) VALUES (?, ?)", (projectID, member,))
        
        db.commit()
        
        flash("Project created!")
        return redirect("/control/projects")
    else:
        if session['role'] == 'admin':
            # Creates a list of managers
            managers = []
            sManagers = cursor.execute("SELECT id, first_name, last_name FROM users WHERE role='manager' AND company_id = ?", (session['company'],)).fetchall()
            for i in sManagers:
                managers.append({
                    'id': i[0],
                    'name': i[1] + " " + i[2]
                })
            
            # Creates a list of projects
            sProjects = cursor.execute("SELECT id, title, status FROM projects WHERE company = ?", (session['company'],)).fetchall()
            projects = []
            for p in sProjects:
                projects.append({
                    'id': p[0],
                    'title': p[1],
                    'status': p[2]
                })
                
            test = projectsPercentage(session['company'])

            return render_template("projects.html", Managers=managers, Projects=test)
        else:
            return redirect('/')
        

@app.route("/projects/", methods=["GET", "POST"])
@login_required
def previewProject():
    if request.method == "POST":
        ProjectID = request.form.get("projectID")
        Title = request.form.get("projectTitle")
        Status = request.form.get("projectStatus")
        
        # userRole = request.form.get("UserRole")
        if session['role'] == 'admin':
            cursor.execute('DELETE FROM assignedprojects WHERE project_id = ?', (ProjectID,))
            
            Managers = request.form.getlist("projectAssign")
            for ManagerID in Managers:
                cursor.execute("INSERT INTO assignedprojects (project_id, manager_id) VALUES (?, ?)", (ProjectID, ManagerID,))
        
        cursor.execute("UPDATE projects SET title=?, status=? WHERE id = ?", (Title, Status, ProjectID,))
        db.commit()
        
        url = "/projects/?project=" + ProjectID
        return redirect(url)
    else:
        # Gets project-ID from url
        projectID = request.args.get("project")
        
        # Checks if URL is valid
        if not projectID:
            return redirect('/')
        
        # Check if project exists
        test_projectCompany = cursor.execute("SELECT company FROM projects WHERE id = ?", (projectID,)).fetchall()
        if not test_projectCompany:
            return redirect('/')
        
        # Only allow access to members of the company that the project is associated with
        if session['company'] != test_projectCompany[0][0]:
            return redirect('/')

        # Gets information about current project
        projectTitle, projectStatus = cursor.execute("SELECT title, status FROM projects WHERE id = ?", (projectID,)).fetchall()[0]
        
        # Gets project supervisors (managers)
        sManagers = cursor.execute("SELECT id, first_name, last_name, email, slack FROM users WHERE id IN (SELECT manager_id FROM assignedprojects WHERE project_id = ?)", (projectID,)).fetchall()
        managers = []
        for i in sManagers:
            managers.append({
                'id': i[0],
                'name': i[1] + " " + i[2],
                'email': i[3],
                'slack': i[4]
            })
        
        # Gets all tickets assigned to project
        sTickets = cursor.execute("SELECT id, title, description, status, priority, type, deadline, date_added, author FROM tickets WHERE project = ?", (projectID,)).fetchall()
        tickets = []
        for i in sTickets:
            tickets.append({
                'ID': i[0],
                'Title': i[1],
                'Description': i[2],
                'Status': i[3],
                'Priority': i[4],
                'Type': i[5],
                'Deadline': i[6],
                'Date_added': i[7],
                'Author': i[8],
            })
        
        # Gives admin control access over project
        if session['role'] == 'admin':
            controlAccess = 1
            
            sMembers = cursor.execute("SELECT id, first_name, last_name FROM users WHERE company_id = ? AND role='manager'", (session['company'],)).fetchall()
            members = []
            for i in sMembers:
                members.append({
                    'id': i[0],
                    'name': i[1] + " " + i[2]
                })
            
            return render_template('projectPreview.html', ProjectTitle=projectTitle, ProjectStatus=projectStatus, ProjectID=projectID, ControlAccess=controlAccess, Members=members, Managers=managers, Tickets=tickets)
        # Gives managers of project access over project
        elif session['role'] == 'manager':
            # Check if manager is a supervisor of the project
            if cursor.execute("SELECT manager_id FROM assignedprojects WHERE project_id = ? AND manager_id = ?", (projectID, session['user_id'],)).fetchall()[0][0]:
                controlAccess = 2
        else:
            controlAccess = 0
        
        return render_template('projectPreview.html', ProjectTitle=projectTitle, ProjectStatus=projectStatus, ProjectID=projectID, ControlAccess=controlAccess, Managers=managers, Tickets=tickets)


@app.route("/tickets/", methods=["GET", "POST"])
@login_required
def previewTicket():
    if request.method == "POST":
        ticketID = request.args.get("ticket")
        url = "/tickets/?ticket=" + ticketID
        return redirect(url)
    else:
        ticketID = request.args.get("ticket")
        
        # Checks if URL is valid
        if not ticketID:
            return redirect('/')
        
        # Redirects admin/manager to their special page
        if session['role'] == 'admin' or session['role'] == 'manager':
            url = "/control/tickets/?ticket=" + ticketID
            return redirect(url)
        
        # Check if ticket exists (Every ticket must be associated with a project)
        test_ticketProject = cursor.execute("SELECT project FROM tickets WHERE id = ?", (ticketID,)).fetchall()
        if not test_ticketProject:
            return redirect('/')
        
        # Only allow access to page to users from the company associated with the ticket
        test_ticketCompany = cursor.execute("SELECT company FROM projects WHERE id=(SELECT project FROM tickets WHERE id = ?)", (ticketID,)).fetchall()[0][0]
        if test_ticketCompany != session['company']:
            return redirect('/')
        
        
        title, description, status, priority, t_type, deadline, time_estimate, author_id, date_added, project_id = cursor.execute("SELECT title, description, status, priority, type, deadline, time_estimate, author, date_added, project FROM tickets WHERE id = ?", (ticketID,)).fetchall()[0]
        first, last = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (author_id,)).fetchall()[0]
        author = first + " " + last
        project = cursor.execute("SELECT title FROM projects WHERE id = ?", (project_id,)).fetchall()[0][0]
        
        comments = []
        r_comments = cursor.execute("SELECT commentor_id, comment, date_added FROM comments WHERE ticket_id = ? ORDER BY date_added DESC", (ticketID,)).fetchall()
        for i in r_comments:
            first, last = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (i[0],)).fetchall()[0]
            date = i[2].split('.')[0]
            comments.append({
               "comment": i[1],
               "commentor": first + " " + last,
               "date": date
            })
            
        assigned = []
        r_assigned = cursor.execute("SELECT first_name, last_name, role, slack, email, id FROM users WHERE id IN (SELECT dev_id FROM assignedtickets WHERE ticket_id = ?)", (ticketID,)).fetchall();
        for i in r_assigned:
            assigned.append({
                "name": i[0] + " " + i[1],
                "role": i[2],
                "slack": i[3],
                "email": i[4],
                "id": i[5]
            })
        
        return render_template("ticketDev.html", TicketID=ticketID, Title=title, Description=description, Status=status, Priority=priority, Type=t_type, Deadline=deadline, Estimate=time_estimate, Author=author, DateAdded=date_added, ProjectID=project_id, Project=project, Comments=comments, Assigned=assigned)


@app.route("/control/tickets/", methods=["GET", "POST"]) #/admin/tickets/
@login_required
def previewTicketAdmin():
    if request.method == "POST":
        ticketID = request.form.get("ticket-ID")
        newTitle = request.form.get("ticket-Title")
        newDescription = request.form.get("ticket-Description")
        newType = request.form.get("ticket-Type")
        newStatus = request.form.get("ticket-Status")
        newPriority = request.form.get("ticket-Priority")
        newDeadline = request.form.get("ticket-Deadline")
        newEstimate = request.form.get("ticket-TimeEstimate")
        newProject = request.form.get("ticket-Projects")
        
        # Sets updated values to ticket
        cursor.execute("UPDATE tickets SET title=?, description=?, type=?, status=?, priority=?, deadline=?, time_estimate=?, project=? WHERE id = ?", (newTitle, newDescription, newType, newStatus, newPriority, newDeadline, newEstimate, newProject, ticketID,))
                
        # Removes any former team member assigned to ticket
        cursor.execute("DELETE FROM assignedtickets WHERE ticket_id = ?", (ticketID,))
        
        # Assigns selected members to ticket
        newAssign = request.form.getlist("ticket-Assign")
        for member in newAssign:
            cursor.execute("INSERT INTO assignedtickets (ticket_id, dev_id) VALUES (?, ?)", (ticketID, member,))
        
        db.commit()
        
        url = "/control/tickets/?ticket=" + ticketID
        return redirect(url)
    else: 
        ticketID = request.args.get("ticket")
        
        # Validates access to admins or managers only
        if session['role'] == 'dev' or session['role'] == 'tester':
            url = "/tickets/?ticket=" + ticketID
            return redirect(url)
        
        if session['role'] == 'admin':
            controlAccess = 1
        elif session['role'] == 'manager':
            controlAccess = 2
        
        # Checks if URL is valid
        if not ticketID:
            return redirect('/')
        
        # Check if ticket exists (Every ticket must be associated with a project)
        test_ticketProject = cursor.execute("SELECT project FROM tickets WHERE id = ?", (ticketID,)).fetchall()
        if not test_ticketProject:
            return redirect('/')
        
        # Only allow access to page to users from the company associated with the ticket
        test_ticketCompany = cursor.execute("SELECT company FROM projects WHERE id=(SELECT project FROM tickets WHERE id = ?)", (ticketID,)).fetchall()[0][0]
        if test_ticketCompany != session['company']:
            return redirect('/')
        
        title, description, status, priority, t_type, deadline, time_estimate, author_id, date_added, project_id = cursor.execute("SELECT title, description, status, priority, type, deadline, time_estimate, author, date_added, project FROM tickets WHERE id = ?", (ticketID,)).fetchall()[0]
        first, last = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (author_id,)).fetchall()[0]
        author = first + " " + last
        project = cursor.execute("SELECT title FROM projects WHERE id = ?", (project_id,)).fetchall()[0][0]
        
        comments = []
        r_comments = cursor.execute("SELECT commentor_id, comment, date_added FROM comments WHERE ticket_id = ? ORDER BY date_added DESC", (ticketID,)).fetchall()
        for i in r_comments:
            first, last = cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (i[0],)).fetchall()[0]
            date = i[2].split('.')[0]
            comments.append({
               "comment": i[1],
               "commentor": first + " " + last,
               "date": date
            })
            
        assigned = []
        r_assigned = cursor.execute("SELECT first_name, last_name, role, slack, email, id FROM users WHERE id IN (SELECT dev_id FROM assignedtickets WHERE ticket_id = ?)", (ticketID,)).fetchall();
        for i in r_assigned:
            assigned.append({
                "name": i[0] + " " + i[1],
                "role": i[2],
                "slack": i[3],
                "email": i[4],
                "id": i[5]
            })
        
        projects = []
        projects_raw = cursor.execute('SELECT id, title FROM projects WHERE company = ?', (session['company'],)).fetchall()
        for i in projects_raw:
            projects.append({
                'id': i[0],
                'title': i[1]
            })
        
        members = []
        members_raw = cursor.execute("SELECT id, first_name, last_name, role FROM users WHERE role='dev' OR role='tester' AND company_id = ?", (session['company'],)).fetchall()
        for i in members_raw:
            members.append({
                'id': i[0],
                'name': i[1] + " " + i[2],
                'role': i[3]
            })
        
        return render_template("ticketAdmin.html", ControlAccess=controlAccess, TicketID=ticketID, Title=title, Description=description, Status=status, Priority=priority, Type=t_type, Deadline=deadline, Estimate=time_estimate, Author=author, DateAdded=date_added, ProjectID=project_id, Project=project, Comments=comments, Assigned=assigned, Projects=projects, Members=members)


@app.route("/control/update/ticket", methods=["POST"]) #/tickets/update
def updateTicket():
    ticketID = request.form.get("ticket-ID")
    newType = request.form.get("ticket-Type")
    newStatus = request.form.get("ticket-Status")
    newPriority = request.form.get("ticket-Priority")
    
    cursor.execute('UPDATE tickets SET type=?, status=?, priority=? WHERE id = ?', (newType, newStatus, newPriority, ticketID,))
    db.commit()
    
    url = "/tickets/?ticket=" + ticketID
    return redirect(url)


@app.route("/tickets/comment", methods=["POST"])
def postComment():
    ticketid = request.form.get("ticketIDcomment")
    comment = request.form.get("commentText")
    cursor.execute("INSERT INTO comments (ticket_id, commentor_id, comment, date_added) VALUES (?, ?, ?, ?)", (ticketid, session['user_id'], comment, datetime.datetime.now(),))
    db.commit()
    url = "/tickets/?ticket=" + ticketid
    return redirect(url)