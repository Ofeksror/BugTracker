CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    password_hash TEXT NOT NULL,
    slack TEXT,
    role TEXT,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    status TEXT,
    priority TEXT,
    type TEXT,
    deadline DATE,
    time_estimate INTEGER,
    author INTEGER,
    date_added TIMESTAMP,
    project INTEGER,
    accepted BIT DEFAULT 0,
    FOREIGN KEY(author) REFERENCES users(id)
    FOREIGN KEY(project) REFERENCES projects(id)
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    company INTEGER,
    title TEXT,
    status TEXT,
    FOREIGN KEY(company) REFERENCES companies(id)
);

CREATE TABLE assignedtickets (
    ticket_id INTEGER,
    dev_id INTEGER,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id),
    FOREIGN KEY(dev_id) REFERENCES users(id)
);

CREATE TABLE assignedprojects (
    project_id INTEGER,
    dev_id INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(dev_id) REFERENCES users(id)
);

CREATE TABLE companyprojects (
    project_id INTEGER,
    company_id INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE comments (
    ticket_id INTEGER,
    commentor_id INTEGER,
    comment TEXT,
    date_added TIMESTAMP,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id),
    FOREIGN KEY(commentor_id) REFERENCES users(id)
);