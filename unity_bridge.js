const http = require('http');
const { Server } = require("socket.io");

const httpServer = http.createServer();
const io = new Server(httpServer, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

console.log("🚀 Unity Bridge Server Starting on Port 3000...");

io.on("connection", (socket) => {
    console.log(`✅ Client Connected: ${socket.id}`);

    // Receive command from Web Chatbot
    socket.on("ai_response", (data) => {
        console.log("📩 Received from Chatbot:", data);

        // Broadcast to Unity (assuming Unity listens to 'unity_command')
        // Or just broadcast to everyone else
        socket.broadcast.emit("unity_command", data);
    });

    // Receive status from Unity
    socket.on("unity_status", (data) => {
        console.log("🎮 Received from Unity:", data);
        socket.broadcast.emit("bot_status", data);
    });

    socket.on("disconnect", () => {
        console.log(`❌ Client Disconnected: ${socket.id}`);
    });
});

httpServer.listen(3000, () => {
    console.log("bridge server running on port 3000");
});
