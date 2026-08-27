import React, { useState } from 'react';
import { X, Sparkles, Send, Bot, User } from 'lucide-react';

export default function AIAssistantChat({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Urban Mobility Analyst. Ask me anything regarding road surface defects, hit-and-run ANPR alerts, or transit delay bottlenecks.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { sender: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/assistant/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text })
      });
      const data = await res.json();

      const botMsg = {
        sender: 'bot',
        domain: data.domain,
        summary: data.summary,
        insights: data.insights,
        recommendation: data.actionable_recommendation
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'Error contacting AI backend service. Please try again.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-900/95 backdrop-blur-md border-l border-slate-800 p-6 z-50 flex flex-col shadow-2xl">
      {/* DRAWER HEADER */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">UrbanSense AI Assistant</h3>
            <p className="text-[11px] text-slate-400">Natural language urban query engine</p>
          </div>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* CHAT MESSAGES LOG */}
      <div className="flex-1 py-4 overflow-y-auto space-y-3 text-xs pr-1">
        {messages.map((m, idx) => (
          <div key={idx}>
            {m.sender === 'user' ? (
              <div className="bg-cyan-950/60 border border-cyan-800 p-2.5 rounded-xl ml-4 text-slate-200 space-y-0.5">
                <span className="text-cyan-400 font-semibold flex items-center space-x-1">
                  <User className="w-3 h-3" />
                  <span>You</span>
                </span>
                <div>{m.text}</div>
              </div>
            ) : (
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-xl mr-4 space-y-2">
                <span className="text-cyan-400 font-semibold flex items-center space-x-1">
                  <Bot className="w-3.5 h-3.5" />
                  <span>Urban AI {m.domain ? `(${m.domain})` : ''}</span>
                </span>
                {m.text && <div>{m.text}</div>}
                {m.summary && <div className="font-semibold text-slate-200">{m.summary}</div>}
                {m.insights && (
                  <pre className="text-slate-400 text-[11px] whitespace-pre-wrap font-sans bg-slate-900/80 p-2 rounded">
                    {m.insights}
                  </pre>
                )}
                {m.recommendation && (
                  <div className="text-emerald-400 text-[11px] font-semibold">
                    💡 Action: {m.recommendation}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="text-slate-400 text-xs italic animate-pulse">AI is querying spatial database...</div>
        )}
      </div>

      {/* CHAT INPUT FIELD */}
      <div className="pt-3 border-t border-slate-800 flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question (e.g. Show high severity potholes)..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
        />
        <button
          onClick={handleSend}
          className="p-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-all"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
