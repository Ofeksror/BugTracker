from flask import redirect, session
from functools import wraps
import datetime
import sqlite3

t_db = sqlite3.connect('bugger.db', check_same_thread=False)
# db.row_factory = sqlite3.Row
t_cursor = t_db.cursor()


"""
def login_required(f):
    
    # Decorate routes to require login.

    # https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
"""


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/account/login")
        
        session['company'] = t_cursor.execute('SELECT company_id FROM users WHERE id = ?', (session['user_id'],)).fetchall()[0][0]
        session['role'] = t_cursor.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchall()[0][0]
        t_db.commit()
        
        if session['company'] is None:
            return redirect('/account/wait')
        
        if session['role'] is None:
            return redirect('/account/wait')
        
        return f(*args, **kwargs)
    return decorated_function


def queryToDate(queryDate):
    s = queryDate.split('-')
    y, m, d = int(s[0]), int(s[1]), int(s[2])
    return datetime.datetime(y, m, d)


def projectsPercentage(company):
    sProjects = t_cursor.execute("SELECT id FROM projects WHERE company = ?", (company,)).fetchall()
        
    newProjects = []
    
    for sP in sProjects:
        projectID = sP[0]
        projectStatus = t_cursor.execute("SELECT status FROM projects WHERE id = ?", (sP[0],)).fetchall()[0][0]
        projectTitle = t_cursor.execute("SELECT title FROM projects WHERE id = ?", (sP[0],)).fetchall()[0][0]
        
        percentage = 0
        count = 0

        sTickets =  t_cursor.execute("SELECT project, status FROM tickets WHERE project = ?", (sP[0],)).fetchall()
        for i in sTickets:
            count += 1
            
            if i[1] == 'In Progress':
                percentage += 50
            elif i[1] == 'Resolved':
                percentage += 100

        if count == 0:
            percentDone = 0
        else:
            percentDone = percentage / count
        
        newProjects.append({
            'ID': projectID,
            'Title': projectTitle,
            'Status': projectStatus,
            'Done': percentDone
        })
    
    return newProjects