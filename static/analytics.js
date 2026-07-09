
async function loadData() {
    try {
        const response = await fetch("api/analytics-data");
        if (!response.ok) {
            throw new Error(`HTTP Error! status:${response.status}`);
        }

        const data = await response.json();
        console.log("Successfully retrieved the json package:", data);

        displayDebugData(data);

    } catch(error) {
        console.error("Something went wrong:", error);
    }
}

async function displayDebugData(data) {
    const totalTasks = data.length;
    const completedTasks = data.filter(t => t.isCompleted).length;

    console.log(`There are a total of ${totalTasks} tasks and there are ${completedTasks} completed tasks`);
}

loadData();