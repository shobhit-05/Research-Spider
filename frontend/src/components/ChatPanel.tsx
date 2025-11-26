import { useState } from "react";
import { claudeChat } from "../api";
import { PaperMetadata } from "../types";

interface Props {
  selected: PaperMetadata | null;
  related: PaperMetadata[];
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPanel({ selected, related }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async () => {
    if (!selected || !input.trim()) return;
    const userMessage: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);
    try {
      const response = await claudeChat(selected, related, userMessage.content);
      setMessages((prev) => [...prev, { role: "assistant", content: response.answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Chat failed. Please try again." },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="glass p-4 rounded-xl space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Claude Q&A</h3>
        {!selected && <p className="text-sm text-slate-400">Select a paper to chat</p>}
      </div>
      <div className="h-48 overflow-y-auto space-y-2 pr-1">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`p-2 rounded-lg ${
              m.role === "user" ? "bg-slate-800 text-white" : "bg-slate-900 text-slate-200"
            }`}
          >
            <p className="text-xs uppercase tracking-wide text-slate-400">{m.role}</p>
            <p className="text-sm whitespace-pre-wrap">{m.content}</p>
          </div>
        ))}
        {isTyping && <p className="text-slate-400 text-sm">Claude is thinking...</p>}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!selected}
          className="flex-1 rounded-lg bg-slate-900 border border-slate-700 p-2 focus:border-accent focus:outline-none disabled:opacity-50"
          placeholder="Ask about this paper or its connections"
        />
        <button
          onClick={handleSend}
          disabled={!selected || isTyping}
          className="rounded-lg bg-accent text-black px-4 font-semibold hover:opacity-90 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
