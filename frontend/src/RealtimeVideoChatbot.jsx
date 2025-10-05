import React, { useRef, useState } from "react";

export default function RealtimeVideoChatbot() {
  const [callActive, setCallActive] = useState(false);
  const remoteAudioRef = useRef(null);
  const localVideoRef = useRef(null);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col items-center justify-center p-6">
      <h1 className="text-2xl font-bold mb-4">Realtime Video Chatbot</h1>

      <div className="grid grid-cols-2 gap-4 w-full max-w-4xl">
        {/* Assistant side */}
        <div className="relative rounded-2xl overflow-hidden bg-black aspect-video shadow">
          {/* Audio only, no video */}
          <audio ref={remoteAudioRef} autoPlay playsInline className="hidden" />
          <img
            src="/bitmoji.png"
            alt="Assistant avatar"
            className="w-full h-full object-cover"
          />
          <div className="absolute top-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
            Assistant
          </div>
        </div>

        {/* Your camera */}
        <div className="relative rounded-2xl overflow-hidden bg-black aspect-video shadow">
          <video
            ref={localVideoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-full object-cover"
          />
          <div className="absolute top-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
            You
          </div>
        </div>
      </div>

      <div className="mt-4 space-x-2">
        {!callActive ? (
          <button
            onClick={() => setCallActive(true)}
            className="px-4 py-2 rounded-lg bg-green-600 text-white"
          >
            Start
          </button>
        ) : (
          <button
            onClick={() => setCallActive(false)}
            className="px-4 py-2 rounded-lg bg-red-600 text-white"
          >
            Hang up
          </button>
        )}
      </div>
    </div>
  );
}
