using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using SocketIOClient; // Requires SocketIOClient package
using Newtonsoft.Json.Linq;
using System;

public class UnityAIConnector : MonoBehaviour
{
    public SocketIOUnity socket;
    public string serverUrl = "http://localhost:3000";

    void Start()
    {
        // Setup Socket.IO
        var uri = new Uri(serverUrl);
        socket = new SocketIOUnity(uri, new SocketIOOptions
        {
            Transport = SocketIOClient.Transport.TransportProtocol.WebSocket
        });

        socket.OnConnected += (sender, e) =>
        {
            Debug.Log("✅ Connected to AI Bridge!");
        };

        socket.On("unity_command", (response) =>
        {
            string text = response.GetValue<string>();
            Debug.Log("📩 Received: " + text);
            
            // Execute on Main Thread
            UnityMainThreadDispatcher.Instance().Enqueue(() =>
            {
                ProcessCommand(text);
            });
        });

        socket.Connect();
    }

    void ProcessCommand(string rawCommand)
    {
        // Format: |UNITY_CMD|{"action":"create","object":"Sofa","color":"Red"}|END_CMD|
        if (rawCommand.Contains("|UNITY_CMD|"))
        {
            try
            {
                int start = rawCommand.IndexOf("|UNITY_CMD|") + "|UNITY_CMD|".Length;
                int end = rawCommand.IndexOf("|END_CMD|");
                string json = rawCommand.Substring(start, end - start);

                var data = JObject.Parse(json);
                string action = data["action"].ToString();
                string objName = data["object"].ToString();
                string color = data["color"].ToString();

                if (action == "create")
                {
                    CreateObject(objName, color);
                }
            }
            catch (Exception e)
            {
                Debug.LogError("Error parsing command: " + e.Message);
            }
        }
    }

    void CreateObject(string name, string colorName)
    {
        GameObject obj = null;

        // Simple Primitive Creation for Demo
        if (name.Contains("Cube") || name.Contains("Table")) obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        else if (name.Contains("Sphere") || name.Contains("Chair")) obj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        else if (name.Contains("Capsule") || name.Contains("Sofa")) obj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        else obj = GameObject.CreatePrimitive(PrimitiveType.Cube);

        if (obj != null)
        {
            // Position randomly
            obj.transform.position = new Vector3(UnityEngine.Random.Range(-5, 5), 1, UnityEngine.Random.Range(-5, 5));
            
            // Apply Color
            Renderer rend = obj.GetComponent<Renderer>();
            if (rend != null)
            {
                rend.material.color = GetColor(colorName);
            }
            
            Debug.Log($"✨ Created {name} with color {colorName}");
        }
    }

    Color GetColor(string colorName)
    {
        switch (colorName.ToLower())
        {
            case "red": return Color.red;
            case "blue": return Color.blue;
            case "green": return Color.green;
            case "yellow": return Color.yellow;
            case "black": return Color.black;
            case "white": return Color.white;
            default: return Color.white;
        }
    }
}
