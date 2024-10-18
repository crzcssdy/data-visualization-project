let data;
let selectedYear = "2014";
let selectedMetric = "fertility_rate";
let selectedCountries = [];

async function fetchData() {
    const response = await fetch('fertility_gdp_2014_2024.json');
    data = await response.json();
    populateCountryDropdown();
    updateChoroplethMap();
    updateScatterPlot();
    updateLineChart();
    updateBarChart();
}

// Populate the country dropdown based on available countries in the data
function populateCountryDropdown() {
    const countryDropdown = document.getElementById('country');
    const uniqueCountries = [...new Set(data.map(d => d["Country Name"]))];

    uniqueCountries.forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        option.text = country;
        countryDropdown.appendChild(option);
    });

    // Set default selected countries (first few in the list)
    selectedCountries = uniqueCountries.slice(0, 10);
}

// Function to update the Choropleth Map
function updateChoroplethMap() {
    let filteredData = data.filter(d => d.Year === parseInt(selectedYear));
    
    let metricData = filteredData.map(d => ({
        country: d["Country Name"],
        code: d["Country Code"],
        value: selectedMetric === 'fertility_rate' ? d["Fertility Rate"] : d["GDP"]
    }));

    const map = L.map('choropleth-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    metricData.forEach(country => {
        const color = country.value > 4 ? 'red' : 'green'; // Basic color coding
        L.circle([Math.random() * 100 - 50, Math.random() * 360 - 180], {
            color: color,
            radius: 50000
        }).addTo(map).bindPopup(`${country.country}: ${country.value}`);
    });
}

// Function to update the Scatter Plot
function updateScatterPlot() {
    let filteredData = data.filter(d => d.Year === parseInt(selectedYear) && d["Series Name_y"] === "GDP per capita (current US$)");
    if (selectedCountries.length > 0) {
        filteredData = filteredData.filter(d => selectedCountries.includes(d["Country Name"]));
    }

    let xValues = filteredData.map(d => d.GDP);
    let yValues = filteredData.map(d => d["Fertility Rate"]);
    let countryNames = filteredData.map(d => d["Country Name"]);

    let trace = {
        x: xValues,
        y: yValues,
        text: countryNames,
        mode: 'markers',
        type: 'scatter'
    };

    let layout = {
        title: 'Fertility vs GDP',
        xaxis: { title: 'GDP per Capita (US$)' },
        yaxis: { title: 'Fertility Rate' }
    };

    Plotly.newPlot('scatter-plot', [trace], layout);
}

// Function to update the Line Chart (Global Trends + Selected Countries)
function updateLineChart() {
    // Global average trend
    const globalData = d3.rollup(
        data,
        v => d3.mean(v, d => selectedMetric === 'fertility_rate' ? d["Fertility Rate"] : d["GDP"]),
        d => d.Year
    );

    const globalTrace = {
        x: Array.from(globalData.keys()),
        y: Array.from(globalData.values()),
        mode: 'lines',
        name: 'Global Average',
        line: { color: 'blue' }
    };

    let countryTraces = selectedCountries.map(country => {
        let countryData = data.filter(d => d["Country Name"] === country);
        let years = countryData.map(d => d.Year);
        let values = countryData.map(d => d[selectedMetric === 'fertility_rate' ? "Fertility Rate" : "GDP"]);

        return {
            x: years,
            y: values,
            type: 'scatter',
            mode: 'lines',
            name: country
        };
    });

    let layout = {
        title: 'Trends Over Time (Global + Selected Countries)',
        xaxis: { title: 'Year' },
        yaxis: { title: selectedMetric === 'fertility_rate' ? 'Fertility Rate' : 'GDP per Capita' }
    };

    Plotly.newPlot('line-chart', [globalTrace, ...countryTraces], layout);
}

// Function to update the Bar Chart (Top 10 Countries by Fertility Rate)
function updateBarChart() {
    let filteredData = data.filter(d => d.Year === parseInt(selectedYear) && selectedMetric === 'fertility_rate');

    // Sort by fertility rate and take top 10 countries
    let sortedData = filteredData.sort((a, b) => b["Fertility Rate"] - a["Fertility Rate"]).slice(0, 10);

    let countryNames = sortedData.map(d => d["Country Name"]);
    let fertilityRates = sortedData.map(d => d["Fertility Rate"]);

    let trace = {
        x: countryNames,
        y: fertilityRates,
        type: 'bar'
    };

    let layout = {
        title: 'Top 10 Countries by Fertility Rate',
        xaxis: { title: 'Country' },
        yaxis: { title: 'Fertility Rate' }
    };

    Plotly.newPlot('bar-chart', [trace], layout);
}

// Update year when user changes the dropdown
function updateYear() {
    selectedYear = document.getElementById("year").value;
    updateChoroplethMap();
    updateScatterPlot();
    updateLineChart();
    updateBarChart();
}

// Update metric when user changes the dropdown
function updateMetric() {
    selectedMetric = document.getElementById("metric").value;
    updateChoroplethMap();
    updateScatterPlot();
    updateLineChart();
    updateBarChart();
}

// Update countries when user changes the dropdown
function updateCountries() {
    const countryDropdown = document.getElementById("country");
    selectedCountries = Array.from(countryDropdown.selectedOptions).map(option => option.value);
    updateScatterPlot();
    updateLineChart();
}

window.onload = fetchData;
