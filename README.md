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
    
---

# Pages

### Login Page
  Click on ```Demo Account``` to login as one of the three demo users - The admin, manager or developer.
 
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
    

---

# Usage


