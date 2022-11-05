# Bug Tracker Website
Everything we want to create, practicularily in programming, is a lot more than a todo list item that we can simply check off.
An idea, is most of the time too big and too vague for us to simply act upon it.
That's why, we prefer boiling an idea into smaller, actionable steps. These steps we can ideed check off in our todo list.
So we start by dividing our big idea into smaller projects.
Those projects are still a bit vague, so we go even deeper and divide every small project into smaller, actionable tasks, or - tickets.

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
    
---

# Pages

### Login Page
  Easily log in to your account by filling your email address and password. If you dont have an account - click on create a new user to sign up.
  You can also click on ```Demo Account``` to login as one of the three demo users - The admin, manager or developer.

### Dashboard
  The dashboard looks different depending on your role.
  - **ADMIN**
    
    The admin's dashboard gives him an overview and understanding of the projects of the company.
    - Kanban board
    
      Display of the company's projects in cards sorted by status.
      Each project card contains the title and the approximate start and end date of the project,
      which is calculated by the earliest start date and the latest deadline out of the tickets of the project. 
      When any of the projects is clicked - it will bring you to the corresponding page of the project
      
    - Gantt chart
      
      In this section the admin can see visually the approximate start and end dates of each project in a Gantt chart.
      A minor detail would be the brightness of each project's block - which 0, 50, or 100% of the block is darker based on the status of the project.
      
      A project with an 'Open' status would be a bright color.
      
      A project with an 'In Progress' status would be 50% dark color and 50% bright color.
      
      A project with an 'Closed' status would be 100% dark color.
    
    - Projects gallery
      
      A gallery of cards containing the company's projects and their status
      To get a better understanding of the projects progression there is a progress bar for each project, that is showing you the closest estimation
      to the projects completion by calculating the average percentage completed for the project.
      The method used: Skimming through all of the tickets for each project, we add to variable either 0, 50 or 100 depending of each ticket's status:
      An open ticket - 0, an in-progress ticket 50, and a closed ticket 100. We count the tickets and divide the sum by the count, giving us a pretty
      accurate estimation of the actual completion of the project.
  
  - **MANAGER**
    
    The managers's dashboard gives him an overview of the projects he is assigned.
    - Kanban board
    
      Display of all of the tickets from all of the projects assigned to the manager.
      The tickets are displayed as cards, containing the ticket's title, project, deadline (if any), its urgency and its type.
      The ticket cards are sorted to the kanban board based on their status - open, closed or in-progress.
      Click on any of the tickets to get to the ticket's page.
      
    - Gantt chart
      
      In this section the manager can see visually the all of the tickets of the projects he is assigned to, in a Gantt chart.
      Each ticket gets its own block, that starts at the date the ticket was created and ends at the ticket's deadline.
      Note that only tickets that have a deadline are shown in this chart.
      A minor detail would be the brightness of each project's block - which 0, 50, or 100% of the block is darker based on the status of the ticket.
      
      A ticket with an 'Open' status would be a bright color.
      
      A ticket with an 'In Progress' status would be 50% dark color and 50% bright color.
      
      A ticket with an 'Closed' status would be 100% dark color.
    
    - Projects gallery
      
      A gallery of cards containing the projects assigned to the manager and their status
      To get a better understanding of the projects progression there is a progress bar for each project, that is showing you the closest estimation
      to the projects completion by calculating the average percentage completed for the project.
      
      The method used: Skimming through all of the tickets for each project, we add to variable either 0, 50 or 100 depending of each ticket's status:
      An open ticket - 0, an in-progress ticket 50, and a closed ticket 100. We count the tickets and divide the sum by the count, giving us a pretty
      accurate estimation of the actual completion of the project.
      
  - **DEVELOPER / TESTER**
    
    The developer's dashboard is designed for optimal focus.
    - Kanban board
    
      Display of all of the tickets assigned to the developer.
      The tickets are displayed as cards, containing the ticket's title, project, deadline (if any), its urgency and its type.
      The ticket cards are sorted to the kanban board based on their status - open, closed or in-progress.
      Click on any of the tickets to get to the ticket's page.
      
    - Gantt chart
      
      In this section the developer can see visually all of the tickets assigned to him in a Gantt chart.
      Each ticket gets its own block, that starts at the date the ticket was created and ends at the ticket's deadline.
      Note that only tickets that have a deadline are shown in this chart.
      A minor detail would be the brightness of each project's block - which 0, 50, or 100% of the block is darker based on the status of the ticket.
      
      A ticket with an 'Open' status would be a bright color.
      
      A ticket with an 'In Progress' status would be 50% dark color and 50% bright color.
      
      A ticket with an 'Closed' status would be 100% dark color.

### Ticket page
  A ticket page is a page displaying all of the information regarding a certain ticket, allowing members with permission to update it.
  
  The page displays the ticket's details mostly using color-coded badges.
  
  When you hover over the 'Project' button it will show you the title of the project the ticket is associated with.
  When clicked, you will be redirected to the project's page.
  
  A user can click on 'Update Ticket' and depending on the user's role, he will have different options to change.
  
  The comments section allows users to easily post short updates, questions or anything they have in mind to share with the team.
  
  The members section lists the developers and testers assigned to work on the ticket.
  When clicked, a modal will pop up and show you the contact information of the member.

### Project page
  The project page enables company members to see each project's details and its tickets.
  The title of the project and its status is displayed in bold.
  
  A manager would be able to update the project's status.
  An admin would be able to update, add or remove the project's assigned managers.
  
  The project page shows a gallery of all of the tickets of the project, and of course when clicked, you will be redirected to the page of the ticket you selected.

### Tickets (Admin)
  Only an admin can access the tickets page.
  The page contains two tables - the uunaccepted tickets and the accepted tickets.
  
  *Unaccepted tickets* are tickets reported by developers or testers, that the admin can accept to approve the ticket and assign developers and testers for this ticket.
  The unaccepted tickets can be modified before being accepted - the deadline, title, description, priority - every detail can be changed before accepting. 
  The unaccepted tickets can also be deleted.
  
  *Accepted tickets* are tickets that are already up and running.
  Click on any of the tickets to open the modal for editing and changing anything about the ticket.
  Although if you want to assign team members to work on the ticket or post comments, you need to click on 'Manage Team' to be redirected to the ticket's page.

### Projects (Admin)
  Only an admin can access the projects page.
  The page contains a gallery of projects. Each project is a card, displaying its project's name, status, and percentage completed
  that is calculated using the same methods as used in the dashboard.
  
  When any of the cards is clicked, it will bring you to the project's page.
  
  An admin can create a new project by clicking on the 'New Project' button. He will be asked to give the project a title, a status, and assign managers to it.
  To assign more than one manager, Ctrl + Click on the managers select menu.

### Team (Admin)
  Only an admin can access the team management page.
  The team management page allows an admin to control his company members, updating member's role, removing them from the company,
  or inviting new members into the   company.
  
  The form at the top requests an email address of a new member you want to invite. Then select the role you want to assign to this user and click Invite.
  
  Any of the cards of the company members will show you the member's name, email address and role.
  When you click any of them a modal will be opened, showing you the same information, and the member's slack, if he has one.
  You can change the member's role and click on 'Save changes' for it to update.
