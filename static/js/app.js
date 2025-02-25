let lastValidData = {};

function fetchData() {
    fetch('/get_data')
    .then(response => response.json())
    .then(data => {
        let container = document.getElementById("data-container");
        container.innerHTML = ""; 

        // Group data into categories
        let categories = {
            "Voltage": ["L1 Phase Voltage", "L2 Phase Voltage", "L3 Phase Voltage", "L1/L2 Voltage", "L2/L3 Voltage", "L3/L1 Voltage"],
            "Current": ["L1 Current", "L2 Current", "L3 Current", "Neutral Current"],
            "Frequency & Harmonic": ["L1 Frequency", "L1 (%)THD Voltage", "L2 (%)THD Voltage", "L3 (%)THD Voltage", "L1 (%)THD Current", "L2 (%)THD Current", "L3 (%)THD Current"],
            "Power": ["Active 3-Phase Power", "Apparent 3-Phase Power", "3-Phase Power Factor", "Consume Active Energy"],
            // "Frequency & Harmonic": ["L1 Frequency", "L1 (%)THD Voltage", "L2 (%)THD Voltage", "L3 (%)THD Voltage", "L1 (%)THD Current", "L2 (%)THD Current", "L3 (%)THD Current"]
        };

        // Create cards for each category
        Object.keys(categories).forEach(category => {
            let groupDiv = document.createElement("div");
            groupDiv.classList.add("data-group");

            let title = document.createElement("h2");
            title.textContent = category;
            groupDiv.appendChild(title);

            categories[category].forEach(key => {
                let value = data[key] !== null ? data[key] : (lastValidData[key] || "N/A");
                lastValidData[key] = value;  // Store last valid value

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

// Fetch data every 2 seconds (2000 milliseconds)
setInterval(fetchData, 2000);

// Fetch data immediately on page load
window.onload = fetchData;
