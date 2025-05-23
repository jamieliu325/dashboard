const express = require('express');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const axios = require('axios');

const app = express();

// Serve static files (including dashboard.html)
app.use(express.static('.'));

// Route for the root path
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// read data from csv and popup with marker on map
app.get('/csv_water_level', (req, res) => {
    const dataPath = 'data/data.csv';
    const results = [];

    fs.createReadStream(dataPath)
        .pipe(csv())
        .on('data', (data) => results.push(data))
        .on('end', () => {
            if (results.length > 0) {
                const firstRow = results[0];
                const water_level = parseFloat(firstRow.water_level).toFixed(2);
                const filtered_water_level = parseFloat(firstRow.filtered_water_level || 0).toFixed(2);

                res.json({
                    water_level: water_level,
                    filtered_water_level: filtered_water_level
                });
            } else {
                res.status(404).json({ error: "No data found" });
            }
        })
        .on('error', (err) => {
            res.status(500).json({ error: "Error reading data file" });
        });
});


// get data from API and popup with circle on map
app.get('/api_water_level', async (req, res) => {
    const apiUrl = "https://api.sealevelsensors.org/v1.0/Datastreams(3)/Observations?$filter=phenomenonTime%20ge%202019-09-19T00:00:00.000Z%20and%20phenomenonTime%20le%202019-09-20T00:00:00.000Z";

    try {
        const response = await axios.get(apiUrl);
        const data = response.data;

        if (data.value && data.value.length > 0) {
            const waterLevel = parseFloat(data.value[0].result).toFixed(2);
            res.json({
                water_level: parseFloat(waterLevel)
            });
        } else {
            res.status(404).json({ error: 'No data found in API response' });
        }

    } catch (error) {
        console.error('API request failed:', error.message);
        res.status(500).json({ error: 'Failed to fetch water level data from API' });
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});