const express = require('express');
const cors = require('cors');
const bodyparser = require('body-parser');
const app = express();

app.use(bodyparser.json({ limit: '50mb' }));
app.use(cors())

app.get('/api/ai/buildings', (req, res) => {
    const buildings = require('./static/buildings.js');
    console.log(JSON.stringify(buildings, null, '\t'));
    res.send(buildings);
});

app.post('/api/ai/create-position-detections', (req, res) => {
    console.log(JSON.stringify(req.body, null, '\t'));
    res.send({ status: true });
});

app.listen(3000, () => console.log('start server...'));