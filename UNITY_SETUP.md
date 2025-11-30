# Unity Integration Guide

## 1. Install Socket.IO for Unity
You need a library to connect Unity to the Node.js server.
1. Open Unity.
2. Go to **Package Manager**.
3. Click **"+"** -> **"Add package from git URL"**.
4. Enter: `https://github.com/itisnajim/SocketIOUnity.git`
5. Click **Add**.

## 2. Add the Script
1. Drag the `UnityAIConnector.cs` file into your Unity Project (Assets folder).
2. Create an **Empty GameObject** in your scene (name it "AI_Manager").
3. Drag the `UnityAIConnector` script onto this GameObject.

## 3. Add Main Thread Dispatcher
Since Socket.IO runs on a separate thread, you need a dispatcher to run Unity commands.
1. Create a new script called `UnityMainThreadDispatcher.cs`.
2. Copy the code from here: [UnityMainThreadDispatcher GitHub](https://github.com/PimDeWitte/UnityMainThreadDispatcher/blob/master/UnityMainThreadDispatcher.cs)
3. Add this script to the same "AI_Manager" object.

## 4. Run!
1. Start the Bridge Server: Run `start_unity_bridge.bat`.
2. Play the Unity Scene.
3. Talk to the Chatbot (e.g., "Add a red sofa").
4. Watch the object appear in Unity!
