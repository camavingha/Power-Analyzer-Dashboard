let logging = false;
let loggedData = [];
let loggingIntervalId = null;

// Start the dashboard update loop immediately
setInterval(fetchData, 2000);
fetchData(); // Fetch data once on page load

document.getElementById("toggle-btn").addEventListener("click", function () {
    logging = !logging;
    this.textContent = logging ? "Stop Logging" : "Start Logging";

    if (logging) {
        loggedData = [];
        loggingIntervalId = setInterval(fetchAndLogData, 2000);
    } else {
        clearInterval(loggingIntervalId);
        document.getElementById("export-btn").disabled = false; // Enable export
    }
});

// Fetch and update dashboard display
function fetchData() {
    fetch('/get_data')
        .then(response => response.json())
        .then(data => {
            let container = document.getElementById("data-container");
            container.innerHTML = ""; 

            let categories = {
                "Voltage": ["L1 Phase Voltage", "L2 Phase Voltage", "L3 Phase Voltage", "L1/L2 Voltage", "L2/L3 Voltage", "L3/L1 Voltage"],
                "Current": ["L1 Current", "L2 Current", "L3 Current", "Neutral Current"],
                "Frequency & Harmonic": ["L1 Frequency", "L1 (%)THD Voltage", "L2 (%)THD Voltage", "L3 (%)THD Voltage", "L1 (%)THD Current", "L2 (%)THD Current", "L3 (%)THD Current"],
                "Power": ["Active 3-Phase Power", "Apparent 3-Phase Power", "3-Phase Power Factor", "Consume Active Energy"]
            };

            Object.keys(categories).forEach(category => {
                let groupDiv = document.createElement("div");
                groupDiv.classList.add("data-group");

                let title = document.createElement("h2");
                title.textContent = category;
                groupDiv.appendChild(title);

                categories[category].forEach(key => {
                    let value = data[key] !== null ? data[key] : "N/A";
                    let item = document.createElement("div");
                    item.classList.add("data-box");
                    item.innerHTML = `<p><strong>${key}:</strong> ${value}</p>`;
                    groupDiv.appendChild(item);
                });

                container.appendChild(groupDiv);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Fetch and log data
function fetchAndLogData() {
    fetch('/get_data')
        .then(response => response.json())
        .then(data => {
            let timestamp = new Date().toISOString();
            let entry = { timestamp, ...data };
            loggedData.push(entry);
        })
        .catch(error => console.error('Error logging data:', error));
}

document.getElementById("export-btn").addEventListener("click", function () {
    let format = document.getElementById("export-format").value;

    if (format === "pdf") {
        captureScreenshot();  // New function for PDF
    } else {
        fetch(`/export?format=${format}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(loggedData)
        })
        .then(response => response.blob())
        .then(blob => {
            let link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = `export.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        })
        .catch(error => console.error('Export Error:', error));
    }
});

function captureScreenshot() {
    html2canvas(document.body).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const { jsPDF } = window.jspdf;
        let pdf = new jsPDF("portrait", "mm", "a4");

        let imgWidth = 210; // A4 width in mm
        let imgHeight = (canvas.height * imgWidth) / canvas.width;

        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        pdf.save("dashboard_screenshot.pdf");
    });
}