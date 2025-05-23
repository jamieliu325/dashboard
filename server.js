const express = require('express');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

const app = express();

// Serve static files (including dashboard.html)
app.use(express.static('.'));

// Route for the root path
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Route for water level data
app.get('/water_level', (req, res) => {
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

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});