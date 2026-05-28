
// ======= MODALS =======
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none'
}
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block'
}

// ======= TASK FUNCTIONS =======
function addTask(formElement) {
    // this sends a form to the flask api, which flask will read in request.form.get("due_date")
    const formData = new FormData();
    formData.append('content', formElement.querySelector('[name="content"]').value);
    formData.append('priority', formElement.querySelector('[name="priority"]').value);
    formData.append('due_date', formElement.querySelector('[name="due_date"]').value);

    fetch('/add', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // connects witht 'jsonify' in the routing file
    .then(data => {
        if (data.success) {
            window.location.reload();

        } else {
            alert('Something went wrong: ' + data.error);
        }
    });

}


function deleteTask(taskId, btnElement) {
    if (!confirm('Are you sure want to delete this task?')) return;

    fetch(`/delete_task/${taskId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Climbs up / traverse the DOM (HTML) tree to find the task card and remove it
            // The .closest() method finds the nearest instance of a '.task-card' in the html file, which is where the delete btn lives
            const taskCard = btnElement.closest('.task-card');
            taskCard.remove();

        } else {
            alert('Something went wrong: ' + data.error);
        }
    });
}
// As a note: if the class starts with a period (.) => html element
// if it does not => css object

function updateTask(taskId, btnElement) {
    fetch(`/update_task/${taskId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const taskCard = btnElement.closest('.task-card');

            // toggle the visuals of the class 'task-done' - classList is a list of the all classes
            // in the html file
            taskCard.classList.toggle('task-done', data.isCompleted);

            // Update the status text
            // span is a html element
            const statusSpan = taskCard.querySelector('.task-status');
            // the ? means the first value is returned if data.isCompleted is true;
            // it returns the second value otherwise
            statusSpan.textContent = `| Status: ${data.isCompleted ? 'Done' : 'Pending'}`;

        } else {
            alert("something went wrong: " + data.error);''
        }
    })
    }

function openEditModal(taskId, content, priority, dueDate) {
    // Populate the form fields with the task's current values
    document.getElementById('edit-content').value = content;
    document.getElementById('edit-priority').value = priority;
    document.getElementById('edit-due-date').value = dueDate;

    // Set the save button to call editTask with the task's id
    document.getElementById('edit-save-btn').onclick = () => editTask(taskId, document.getElementById('editModal'));
    // () => is a shorthand way to define a function
    // it is used here as we want to CALL a function not RETURN the value of the function (None)

    openModal('editModal');
}

// modalElement here means the function takes in the modal/form (where the user changes the values)
// and then extracts the new values (for content, due date, and priority)
function editTask(taskId, modalElement) {
    // 1. new keyword is needed when creating new instances of a class (allocating memory for the instance)
    // 2. FormData() mimics a html form being submitted, allowing us to send data via fetch
    // to update the UI of the task card
    // => same structure (but built manually) as flask request.form.get(...)
    const formData = new FormData();

    // .value is a property of the html element (every html element is represented as a JavaScipt object)
    // every JS object has properties, and 'value' => the real-time text inside the input
    formData.append('content', modalElement.querySelector('[name="content"]').value);
    formData.append('priority', modalElement.querySelector('[name="priority"]').value);
    formData.append('due_date', modalElement.querySelector('[name="due_date"]').value);


    fetch(`/edit_task/${taskId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // const because it doesn't the task card will always have the same id
            const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);

            taskCard.classList.toggle('task-overdue', data.isOverdue);

            // const is important as it prevents the variables from being persistent global variables,
            // which we do not need as they should be local to the function
            const contentH = taskCard.querySelector('.task-content');
            const prioritySpan = taskCard.querySelector('.task-priority');
            const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High'};
            const dueSpan = taskCard.querySelector('.task-due');

            // removes the old priority and add the new one depending on the selected priority
            taskCard.classList.remove('priority-low', 'priority-medium', 'priority-high');
            taskCard.classList.add(`priority-${priorityMap[data.priority].toLowerCase()}`);

            contentH.textContent = data.content;
            // ?? (nullish coalescing operator) => returns 'Not Set' only if the left side returns null/undefined
            prioritySpan.textContent = `| Priority: ${priorityMap[data.priority] ?? 'Not Set'}`;
            dueSpan.textContent = data.dueDate;

            closeModal('editModal');

        } else {
            alert("Something went wrong: " + data.error);
        }
    })
}


// ======= TIMER =======

let timeLeft = INITIAL_TIMER * 60;
let timerInterval;  

function updateDisplay() {
    const mins = Math.floor(timeLeft / 60)
    const secs = timeLeft % 60;
    document.getElementById('timer-display').innerText =
    `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function setTimer(minutes){
    timeLeft = minutes * 60
    updateDisplay()

    // Save this choice to the database
    fetch('/update_last_timer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ minutes: minutes })
    });
}
    
function startTimer() {
    if (timerInterval) return;
    timerInterval = setInterval(() => {
        if (timeLeft > 0) {
            timeLeft--;
            updateDisplay();
        } else {
            clearInterval(timerInterval);
            timerInterval = null;
            alert("Time for a break!");
        }
    }, 1000)
}
function resetTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    timeLeft = INITIAL_TIMER * 60;
    updateDisplay();
}