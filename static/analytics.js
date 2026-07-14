

async function loadData() {
    try {
        const response = await fetch("api/analytics-data");
        if (!response.ok) {
            throw new Error(`HTTP Error! status:${response.status}`);
        }

        const tasks = await response.json();
        console.log("Successfully retrieved the json package:", tasks);

        tasks.forEach(task => {
            console.log("Priority: ", task.priority, "Type: ", typeof task.priority)
        });

        displayDebugData(tasks);

        populateMetrics(tasks);
        renderPriorityChart(tasks);
        renderCompletedPie(tasks);

    } catch(error) {
        console.error("Something went wrong:", error);
    }
}

async function displayDebugData(data) {
    const totalTasks = data.length;
    const completedTasks = data.filter(t => t.isCompleted).length;

    console.log(`There are a total of ${totalTasks} tasks and there are ${completedTasks} completed tasks`);
}

async function populateMetrics(tasks) {
    const total = tasks.length;
    const completed = tasks.filter(t => t.isCompleted).length;
    const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

    document.getElementById("metric-total").innerText = total;
    document.getElementById("metric-completed").innerText = completed;
    document.getElementById("metric-rate").innerText = `${rate}%`;
}

async function renderPriorityChart(tasks) {
    // calculates how many tasks of each type there are
    const counts = { 1: 0, 2: 0, 3: 0 };
    // lambda function that loops through each task
    tasks.forEach(task => {
        if (counts[task.priority] !== undefined) { // exculdes any number outside of 1 to 3
            counts[task.priority]++;
        }
    });

    // take the context object of the canvas -> gives access to the drawing API for the canvas
    const context = document.getElementById("priorityChart").getContext("2d");

    new Chart(context, {
        type: "bar",
        data: {
            labels: ["Low", "Medium", "High"],
            datasets: [{
                label: "Number of Tasks",
                data: [counts[1], counts[2], counts[3]],
                backgroundColor: [
                    "#257941",
                    "#ffd300",
                    "#ad1010"
                ],
                borderWidth: 2,
                borderRadiues: 6
        }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // the ratio/proportion of the height and width of the chart
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 } // increments by 1 since no. of tasks is a whole integer
                }
            }
        }
    })
}

async function renderCompletedPie(tasks) {
    const counts = { 1: 0, 2: 0, 3: 0};
    const completed = tasks.filter(t => t.isCompleted);
    console.log(completed);

    completed.forEach(task => {
        counts[task.priority]++;
    })

    const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
    const percentages = { 1: 0, 2: 0, 3: 0};

    for (let i in percentages) {
        percentages[i] = Math.round((counts[i] / total) * 100)
    };

    const context = document.getElementById("completedChart").getContext("2d");
    const data = {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{
            label: "Completion by Priority",
            data: [percentages[1], percentages[2], percentages[3]],
            backgroundColor: [
                "rgba(6, 244, 109, 0.68)",
                "rgb(255, 234, 0)",
                "rgba(237, 8, 8, 0.9)"
            ],
            borderWidth: 0
        }]
    };

    const config = {
        type: "pie",
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "left",
                    labels: {
                        font: {
                            size: 14,
                            family: '-apple-system, BlinkMacSystemFont, sans-serif',
                            weight: '500'
                        },
                        usePointStyle: true
                    }
                },
                title: {
                    display: false
                }
            }
        }
    };

    new Chart(context, config);
}

loadData();