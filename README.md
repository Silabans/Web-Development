# To-do List Website

This is my first website that I made to learn python modules like Flask and SQLAlchemy for API and backend logic, 
as well as HTML and CSS for the website user interface.

## Tools Used

* Python (base) for handling algorithms like determining high-priority tasks
* Flask (python module) for website routing and request handling
* SQLAlchemy for constructing SQL queries and transforming python classes into SQL databases
* HTML for handling the skeletal structure of the website UI
* CSS for styling and polishing the look of the website UI
* JavaScript for logical flows on the website, such opening modals and task functions

## Status

This project is still a work in progress, though a working version has been deployed.

### Current to-do list:
* Adding a "Productivity Level" section to track the number of tasks completed
  and the amount of time spent using the timer
* ~~Integrating CSS to elevate the UI~~
* ~~adding the "create task" function~~
* ~~adding the sort function that ranks task cards in terms of priority~~
* ~~add a podomoro timer for time-keeping~~

## Challenges faced and tackled:
* CSS objects with conflicting settings (e.g. "New Task" modal and the timer, leading to misplaced elements.
  How it was solved: Ensuring that each element has the correct placement in the HTML framework and using CSS flexbox.
* Insecure passwords.
  How it was solved: Doing password hashing werkzeug.security.
* Migrating frontend structure to JavaScript from purely Flask

