let logging = false;
let loggedData = [];
let loggingIntervalId = null;

// Start the dashboard update loop immediately
setInterval(fetchData, 2000);
fetchData(); // Fetch data once on page load

document.getElementById("toggle-btn").addEventListener("click", function () {
    if (logging) {
        // Stop Logging
        logging = false;
        this.textContent = "Start Logging"; // Change text back to Start
        clearInterval(loggingIntervalId); // Stop the interval
        document.getElementById("export-btn").disabled = false; // Enable export button
        document.getElementById("copy-btn").disabled = false; // Enable copy button
    } else {
        // Start Logging
        logging = true;
        loggedData = []; // Clear previous logs
        this.textContent = "Stop Logging"; // Change text to Stop
        loggingIntervalId = setInterval(fetchAndLogData, 2000); // Start the logging interval
        document.getElementById("export-btn").disabled = true; // Disable export button until stop
        document.getElementById("copy-btn").disabled = true; // Disable copy button until stop
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

// Export data
document.getElementById("export-btn").addEventListener("click", function () {
    let format = document.getElementById("export-format").value;

    if (format === "pdf") {
        captureScreenshot();  // New function for PDF
    } else if (format === "rtf") {
        exportRTF(); // New function for RTF
    } else if (format === "xml") {
        exportXML(); // New function for XML
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

// Capture screenshot for PDF
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

// Export RTF function
function exportRTF() {
    let rtfContent = `{\rtf1\ansi\deff0 {\fonttbl {\f0\fnil\fcharset0 Arial;}}`;
    loggedData.forEach(entry => {
        rtfContent += `\n${entry.timestamp}\n`;
        for (let key in entry) {
            if (key !== "timestamp") {
                rtfContent += `${key}: ${entry[key]}\n`;
            }
        }
        rtfContent += "\n";
    });
    rtfContent += "}";

    let blob = new Blob([rtfContent], { type: 'application/rtf' });
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "export.rtf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Export XML function
function exportXML() {
    let xmlContent = '<?xml version="1.0" encoding="UTF-8"?>\n<logData>';
    loggedData.forEach(entry => {
        xmlContent += `\n  <entry>\n    <timestamp>${entry.timestamp}</timestamp>\n`;
        for (let key in entry) {
            if (key !== "timestamp") {
                xmlContent += `    <${key}>${entry[key]}</${key}>\n`;
            }
        }
        xmlContent += "  </entry>";
    });
    xmlContent += "\n</logData>";

    let blob = new Blob([xmlContent], { type: 'application/xml' });
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "export.xml";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Copy to clipboard function
document.getElementById("copy-btn").addEventListener("click", function () {
    let logText = "";

    // Check if logging is active
    if (!logging && loggedData.length > 0) {
        // Format logged data into a clipboard-friendly format
        loggedData.forEach(entry => {
            logText += `Timestamp: ${entry.timestamp}\n`;
            for (let key in entry) {
                if (key !== "timestamp") {
                    logText += `${key}: ${entry[key]}\n`;
                }
            }
            logText += "\n";
        });

        // Copy the formatted log data to clipboard
        navigator.clipboard.writeText(logText)
            .then(() => {
                alert("Log data copied to clipboard!");
            })
            .catch(err => {
                console.error("Error copying to clipboard", err);
            });
    } else {
        alert("No data to copy. Please stop logging first.");
    }
});
