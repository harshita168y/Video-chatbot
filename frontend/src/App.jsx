import React, { useState, useEffect, useRef } from "react";
import Webcam from "react-webcam";
import { Mic, Square, PhoneOff } from "lucide-react"; // ✅ Added PhoneOff for End Call

export default function App() {
  const [messages, setMessages] = useState([]); 
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [userActive, setUserActive] = useState(false);
  const [greeted, setGreeted] = useState(false);
  const [botTyping, setBotTyping] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [callEnded, setCallEnded] = useState(false); // ✅ End call state

  const recognitionRef = useRef(null);
  const webcamRef = useRef(null);

  useEffect(() => {
    if (callEnded) return; // ✅ Don't send frames if call ended
    const ws = new WebSocket("ws://localhost:8000/video-stream");

    ws.onopen = () => {
      console.log("✅ WebSocket connected for video-stream");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Presence update:", data);

      setUserActive(data.active);

      if (data.active && data.user && !greeted) {
        const greeting = `Hello ${data.user}, how is your day going?`;

        setMessages((prev) => [...prev, { from: "bot", text: greeting }]);

        const synth = window.speechSynthesis;
        const utter = new SpeechSynthesisUtterance(greeting);
        utter.lang = "en-US";
        utter.onstart = () => setIsSpeaking(true);
        utter.onend = () => setIsSpeaking(false);
        synth.speak(utter);

        setGreeted(true);
      }
    };

    ws.onclose = () => {
      console.log("❌ WebSocket closed for video-stream");
    };

    const interval = setInterval(() => {
      if (webcamRef.current && ws.readyState === WebSocket.OPEN) {
        const screenshot = webcamRef.current.getScreenshot();
        if (screenshot) {
          const base64Data = screenshot.split(",")[1];
          ws.send(base64Data);
        }
      }
    }, 500);

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, [greeted, callEnded]);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error("Speech recognition not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = true;

    recognition.onstart = () => {
      console.log("🎤 Listening...");
      setIsListening(true);
    };

    recognition.onend = () => {
      console.log("🛑 Stopped listening.");
      setIsListening(false);
    };

    recognition.onresult = async (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      console.log("Final result:", transcript);

      setMessages((prev) => [...prev, { from: "user", text: transcript }]);

      setBotTyping(true);
      try {
        const res = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: transcript }),
        });
        const data = await res.json();

        setMessages((prev) => [...prev, { from: "bot", text: data.reply }]);

        const synth = window.speechSynthesis;
        const utter = new SpeechSynthesisUtterance(data.reply);
        utter.lang = "en-US";
        utter.onstart = () => setIsSpeaking(true);
        utter.onend = () => setIsSpeaking(false);
        synth.speak(utter);
      } catch (err) {
        console.error("Error sending to backend:", err);
      } finally {
        setBotTyping(false);
      }
    };

    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, []);

  // Mic toggle
  const toggleMic = () => {
    if (!recognitionRef.current) return;
    if (isListening) recognitionRef.current.stop();
    else recognitionRef.current.start();
  };

  // Stop Speaking
  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  // End Call
  const endCall = () => {
    setCallEnded(true);
    window.speechSynthesis.cancel();
    if (recognitionRef.current) recognitionRef.current.stop();
  };

  // Send manual text input
  const send = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { from: "user", text: input }]);
    setBotTyping(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });
      const data = await res.json();

      setMessages((prev) => [...prev, { from: "bot", text: data.reply }]);

      const synth = window.speechSynthesis;
      const utter = new SpeechSynthesisUtterance(data.reply);
      utter.lang = "en-US";
      utter.onstart = () => setIsSpeaking(true);
      utter.onend = () => setIsSpeaking(false);
      synth.speak(utter);
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setBotTyping(false);
    }
    setInput("");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">
      {/* subtle background glow */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[520px] w-[520px] rounded-full bg-indigo-600/20 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-[420px] w-[420px] rounded-full bg-purple-600/20 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-[380px] w-[380px] rounded-full bg-blue-700/20 blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative p-6 text-center border-b border-white/10 bg-gradient-to-b from-slate-900/40 to-transparent">
        <h1 className="text-3xl md:text-4xl font-bold tracking-wide">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-sky-300 to-purple-300">
            Realtime Video Chatbot
          </span>
        </h1>
      </header>

      {/* Video row */}
      <main className="relative flex-1 flex flex-col items-center justify-center p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 w-full max-w-6xl">
          {/* Bot */}
          <section className="relative flex flex-col items-center">
            <h2 className="text-sm uppercase tracking-widest text-slate-300/70 mb-3">
              Bot
            </h2>
            <div className="relative w-full h-72 rounded-2xl overflow-hidden">
              <img
                src="/bitmoji.jpeg"
                alt="Chatbot avatar"
                className="w-full h-full object-cover rounded-2xl"
              />
              {callEnded && (
                <div className="absolute inset-0 bg-slate-900/70 backdrop-blur flex items-center justify-center text-white text-lg font-semibold">
                  Call Ended
                </div>
              )}
            </div>
          </section>

          {/* User */}
          <section className="relative flex flex-col items-center">
            <h2 className="text-sm uppercase tracking-widest text-slate-300/70 mb-3">
              You
            </h2>
            <div className="relative w-full h-72 rounded-2xl overflow-hidden">
              <Webcam
                ref={webcamRef}
                audio={false}
                mirrored={true}
                screenshotFormat="image/jpeg"
                className="w-full h-full object-cover rounded-2xl"
              />
              {callEnded && (
                <div className="absolute inset-0 bg-slate-900/70 backdrop-blur flex items-center justify-center text-white text-lg font-semibold">
                  Call Ended
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Controls */}
        <div className="flex gap-6 mt-10">
          {/* Mic Button */}
          <button
            onClick={toggleMic}
            disabled={callEnded}
            className={`p-5 rounded-full shadow-xl transition ${
              isListening
                ? "bg-emerald-500 hover:bg-emerald-400 ring-8 ring-emerald-500/20"
                : "bg-rose-600 hover:bg-rose-500 ring-8 ring-rose-600/20"
            }`}
          >
            <Mic size={28} />
          </button>

          {/* Stop Speaking */}
          {isSpeaking && !callEnded && (
            <button
              onClick={stopSpeaking}
              className="p-5 rounded-full bg-yellow-500 hover:bg-yellow-400 shadow-xl ring-8 ring-yellow-500/20 transition"
            >
              <Square size={28} />
            </button>
          )}

          {/* End Call */}
          {!callEnded && (
            <button
              onClick={endCall}
              className="p-5 rounded-full bg-red-700 hover:bg-red-600 shadow-xl ring-8 ring-red-700/20 transition"
            >
              <PhoneOff size={28} />
            </button>
          )}
        </div>

        <div className="mt-2 text-sm">
          {isListening ? (
            <span className="text-emerald-400">Listening…</span>
          ) : (
            <span className="text-rose-400">Not listening</span>
          )}
        </div>
      </main>

      {/* Chat area */}
      {!callEnded && (
        <section className="relative bg-slate-950/40 backdrop-blur-md border-t border-white/10 flex flex-col h-96 rounded-t-2xl shadow-inner">
          <h3 className="text-lg font-semibold p-4 border-b border-white/10">
            Chat
          </h3>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-xs p-3 rounded-xl shadow-md transition ${
                  m.from === "bot"
                    ? "bg-gradient-to-r from-indigo-700/60 to-purple-600/60 text-indigo-100"
                    : "bg-gradient-to-r from-sky-500 to-blue-500 text-white ml-auto"
                }`}
              >
                <strong>{m.from === "bot" ? "Bot" : "You"}:</strong> {m.text}
              </div>
            ))}

            {botTyping && (
              <div className="max-w-xs p-3 rounded-xl shadow-md bg-gradient-to-r from-indigo-700/60 to-purple-600/60 text-indigo-100">
                <strong>Bot:</strong>{" "}
                <span className="inline-flex items-center gap-1 ml-1">
                  <span className="h-2 w-2 rounded-full bg-indigo-200 animate-bounce" />
                  <span className="h-2 w-2 rounded-full bg-indigo-200 animate-bounce [animation-delay:120ms]" />
                  <span className="h-2 w-2 rounded-full bg-indigo-200 animate-bounce [animation-delay:240ms]" />
                </span>
              </div>
            )}
          </div>

          {/* Input bar */}
          <form
            onSubmit={send}
            className="flex p-4 border-t border-white/10 bg-slate-950/50 backdrop-blur"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message…"
              className="flex-1 px-3 py-2 rounded-l-xl bg-white/10 border border-white/20 focus:outline-none text-white placeholder-slate-400"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-gradient-to-r from-indigo-500 to-sky-500 hover:opacity-90 text-white rounded-r-xl transition"
            >
              Send
            </button>
          </form>
        </section>
      )}
    </div>
  );
}
