const express = require('express');
const cors = require('cors');
const bodyparser = require('body-parser');
const app = express();

app.use(bodyparser.json({ limit: '50mb' }));
app.use(cors())

app.get('/api/ai/buildings', (req, res) => {
    const buildings = [
        {
            "id": 100001,
            "sniffers": [
                {
                    "id": 100001,
                    "x": 89.45,
                    "y": 34.67
                },
                {
                    "id": 100002,
                    "x": 89.45,
                    "y": 34.67
                },
                {
                    "id": 100003,
                    "x": 89.45,
                    "y": 34.67
                }
            ],
            "areas": [
                {
                    "id": 100001,
                    "location": [
                        [
                            9.8,
                            8.6
                        ],
                        [
                            5.7,
                            23.8
                        ],
                        [
                            35.4,
                            21.7
                        ]
                    ]
                }
            ],
            "raws": [
                {
                    "id": 100001,
                    "id_building": 100001,
                    "mac_hash": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                    "timestamp": "2022-09-09T00:00:00Z",
                    "rssi_device": [
                        [
                            100001,
                            -70
                        ],
                        [
                            100002,
                            -43
                        ],
                        [
                            100003,
                            -15
                        ]
                    ]
                }
            ]
        }
    ];
    console.log(JSON.stringify(buildings, null, '\t'));
    res.send(buildings);
});

app.post('/api/ai/create-position-detections', (req, res) => {
    console.log(JSON.stringify(req.body, null, '\t'));
    res.send({ status: true });
});

app.listen(3000, () => console.log('start server...'));