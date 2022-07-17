# Bug Tracker Website
Everything we want to create, practicularily in programming, isn't just a todo list item that we can simply check off.
An idea, is most of the time too big and too vague for us to simply act upon it.
That's why, we prefer boiling an idea into smaller, actionable steps. These steps we can ideed check off in our todo list.
Come to think about it, we divide each project or big idea into smaller projects.
Those smaller projects are still a bit vague, so we go even deeper and divide a small project into actionable tasks, or - tickets.

---

The website I developed, using Flask as my main framework, helps teams keep track of the progress they make every day towards their big goal.
Each team is a company. Each company, has projects. Each project, has tickets.

Tickets have quite a few attributes
  - Title, Description
  - Type [Bug, Issue, Feature Request, Enhancement]
  - Status [Open, In Progress, Resolved]
  - Priority [Low, Medium, High, Urgent]
  - Deadline
  - Time estimate
  - Project
  - Assigned developers and testers

Projects are built from tickets and have 3 attributes
  - Title
  - Status - [Open, In Progress, Closed]
  - Managers assigned to project

---

The company, or, the team contains 4 roles: 
- Developer / Tester
  - Can report new tickets
  - Can update the type, status, priority of tickets
- Manager
  - Can modify tickets
  - Can manage assigned members for tickets
  - Can update status of projects
  - Can create new tickets
- Admin
  - Can manage the team by adding or removing members from the team, or changing the roles of members
  - Can add or remove new projects
  - Can accept, delete or modify new and existing tickets
  


A user simply registers himself as a new account, filling out his personal information and contact information.
