const express = require('express');
const http = require('http');
const mqtt = require('mqtt');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
    cors: { origin: "http://localhost:3000", methods: ["GET", "POST"] }
});

// Connect to the same MQTT broker your Python script uses
// (Ensure settings.MQTT_BROKER in Python matches this URL)
const mqttClient = mqtt.connect('mqtt://localhost:1883'); 
const MQTT_TOPIC = 'border/alerts';; // Replace with settings.MQTT_TOPIC

mqttClient.on('connect', () => {
    console.log('Backend connected to MQTT Broker');
    mqttClient.subscribe(MQTT_TOPIC, (err) => {
        if (!err) console.log(`Subscribed to topic: ${MQTT_TOPIC}`);
    });
});

// When Python sends an alert, catch it and forward to React
mqttClient.on('message', (topic, message) => {
    if (topic === MQTT_TOPIC) {
        try {
            const alertData = JSON.parse(message.toString());
            console.log('New Alert Received:', alertData.type);
            
            // Push to the React frontend instantly
            io.emit('new_alert', alertData);
            
            // TODO: Later we can add MongoDB code here to save the alert history
        } catch (error) {
            console.error('Error parsing MQTT message:', error);
        }
    }
});

io.on('connection', (socket) => {
    console.log('React Frontend connected to WebSocket');
});

const PORT = 5000;
server.listen(PORT, () => console.log(`Backend running on port ${PORT}`));