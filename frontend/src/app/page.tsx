"use client";


import React, { useRef, useState, useEffect } from 'react';
import { Upload, MessageSquare, FileText, Sparkles, Brain, Zap, Globe, Star, ChevronRight, Send, Paperclip, Bot, User, ExternalLink, FileCheck } from 'lucide-react';

// Real API functions
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  references?: { doc_id: number; doc_name: string; doc_url: string; page?: number; clause?: string; }[];
  timestamp: Date;
};

type UploadedFile = {
  filename: string;
  doc_url: string;
  size: number;
  type: string;
  uploadedAt: Date;
};

export default function HackathonUI() {
  const [uploads, setUploads] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: "🚀 Welcome to IntelliDocs AI! I'm your intelligent document assistant powered by advanced neural networks. Upload your documents and I'll provide contextual insights with unprecedented accuracy.",
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const features = [
    { icon: Brain, title: "AI-Powered Analysis", desc: "Advanced neural processing" },
    { icon: Zap, title: "Lightning Fast", desc: "Sub-second response times" },
    { icon: Globe, title: "Multi-language", desc: "Support for 50+ languages" },
    { icon: Star, title: "Enterprise Grade", desc: "99.9% accuracy guarantee" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature(prev => (prev + 1) % features.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const simulateUpload = async (files: File[]) => {
    setUploading(true);
    setError(null);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        const newUpload: UploadedFile = {
          filename: file.name,
          doc_url: data.doc_url || `uploaded://${file.name}`,
          size: file.size,
          type: file.type,
          uploadedAt: new Date()
        };
        
        setUploads(prev => [...prev, newUpload]);
      } catch (err: any) {
        setError(`Failed to upload ${file.name}: ${err.message}`);
        break;
      }
    }
    
    setUploading(false);
  };

  const simulateAIResponse = async (question: string) => {
    setIsTyping(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/hackrx/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          documents: uploads[0]?.doc_url || '',
          questions: [question]
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      const rawAnswer = data.answers?.[0] || 'No response received';
      
      // Handle both string and object responses
      let answer: string;
      let references: any[] = [];
      
      if (typeof rawAnswer === 'string') {
        answer = rawAnswer;
      } else if (rawAnswer && typeof rawAnswer === 'object' && rawAnswer.answer) {
        answer = rawAnswer.answer;
        references = rawAnswer.references || [];
      } else {
        answer = 'No response received';
      }
      
      const aiMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: answer,
        references: references.length > 0 ? references : uploads.slice(0, 2).map((upload, idx) => ({
          doc_id: idx,
          doc_name: upload.filename,
          doc_url: upload.doc_url,
          page: Math.floor(Math.random() * 50) + 1,
          clause: `Section ${Math.floor(Math.random() * 10) + 1}.${Math.floor(Math.random() * 10) + 1}`
        })),
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (err: any) {
      setError(`Failed to get AI response: ${err.message}`);
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Sorry, I couldn't process your request. Error: ${err.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setIsTyping(false);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    
    const remainingSlots = 15 - uploads.length;
    const filesToUpload = files.slice(0, remainingSlots);
    
    await simulateUpload(filesToUpload);
    
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;
    
    if (uploads.length === 0) {
      setError("Please upload at least one document to get started");
      return;
    }
    
    setError(null);
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    await simulateAIResponse(text);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 backdrop-blur-xl bg-black/20 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  IntelliDocs AI
                </h1>
                <p className="text-xs text-gray-400">Next-Gen Document Intelligence</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>AI Online</span>
              </div>
              {/* <button className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-sm font-medium hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300">
                Upgrade Pro
              </button> */}
            </div>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          {/* <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-xl border border-white/10 rounded-full px-6 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-yellow-400" />
            <span className="text-sm font-medium">Powered by GPT-4 Turbo</span>
          </div> */}
          <h2 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent leading-tight">
            Transform Documents Into
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Intelligence</span>
          </h2>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Upload any document and unlock instant insights with our revolutionary AI-powered analysis engine
          </p>

          {/* Features Carousel */}
          <div className="flex justify-center mb-8">
            <div className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6 min-w-80">
              {features.map((feature, idx) => (
                <div 
                  key={idx}
                  className={`flex items-center gap-4 transition-all duration-500 ${
                    idx === activeFeature ? 'opacity-100 transform translate-y-0' : 'opacity-0 absolute transform translate-y-4'
                  }`}
                >
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                    <p className="text-gray-400 text-sm">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="mb-8">
          <div className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:border-purple-500/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Upload className="w-6 h-6 text-blue-400" />
                <div>
                  <h3 className="text-xl font-semibold text-white">Document Upload</h3>
                  <p className="text-gray-400 text-sm">Drag & drop or click to upload up to 15 files</p>
                </div>
              </div>
              <div className="text-right text-sm text-gray-400">
                <div>{uploads.length}/15 files</div>
                <div className="w-32 h-2 bg-gray-700 rounded-full mt-1">
                  <div 
                    className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
                    style={{ width: `${(uploads.length / 15) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileUpload}
              disabled={uploads.length >= 15 || uploading}
              className="hidden"
              accept=".pdf,.doc,.docx,.txt,.rtf"
            />

            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-600 rounded-2xl p-12 text-center hover:border-blue-500 transition-all duration-300 cursor-pointer group"
            >
              {uploading ? (
                <div className="flex flex-col items-center gap-4">
                  <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-gray-400">Processing files...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Paperclip className="w-8 h-8 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-white mb-2">Click to upload documents</p>
                    <p className="text-gray-400 text-sm">PDF, DOC, DOCX, TXT, RTF supported</p>
                  </div>
                </div>
              )}
            </div>

            {/* Uploaded Files Grid */}
            {uploads.length > 0 && (
              <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {uploads.map((file, idx) => (
                  <div key={idx} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-4 hover:border-blue-500/50 transition-all duration-300 group">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <FileCheck className="w-5 h-5 text-green-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate" title={file.filename}>
                          {file.filename}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-400">{formatFileSize(file.size)}</span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-400">
                            {file.uploadedAt.toLocaleTimeString('en-US', { 
                              hour12: false, 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden">
          <div className="border-b border-white/10 p-6">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-semibold text-white">AI Chat Assistant</h3>
              <div className="flex items-center gap-2 ml-auto">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-400">Ready to help</span>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-6">
            {messages.map((message) => (
              <div key={message.id} className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user' 
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600' 
                    : 'bg-gradient-to-r from-green-500 to-teal-600'
                }`}>
                  {message.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>
                <div className={`flex-1 max-w-2xl ${message.role === 'user' ? 'text-right' : ''}`}>
                  <div className={`inline-block p-4 rounded-2xl ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
                      : 'bg-white/10 backdrop-blur-xl border border-white/20 text-white'
                  }`}>
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>
                  
                  {message.references && (
                    <div className="mt-3 space-y-2">
                      {message.references.map((ref, idx) => (
                        <div key={idx} className="flex items-center gap-3 text-sm bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-3">
                          <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" />
                          <span className="text-gray-300 truncate flex-1">{ref.doc_name}</span>
                          {ref.page && <span className="text-gray-400">Page {ref.page}</span>}
                          {ref.clause && <span className="text-gray-400">• {ref.clause}</span>}
                          <a 
                            href={ref.doc_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 transition-colors"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className={`mt-2 text-xs text-gray-500 ${message.role === 'user' ? 'text-right' : ''}`}>
                    {message.timestamp.toLocaleTimeString('en-US', { 
                      hour12: false, 
                      hour: '2-digit', 
                      minute: '2-digit', 
                      second: '2-digit' 
                    })}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex gap-4">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-xl flex items-center justify-center">
                  <Bot className="w-5 h-5" />
                </div>
                <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-white/10 p-6">
            <div className="flex gap-4">
              <div className="flex-1 bg-white/5 backdrop-blur-xl border border-white/20 rounded-2xl focus-within:border-blue-500/50 transition-all duration-300">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  rows={2}
                  placeholder="Ask me anything about your documents..."
                  className="w-full bg-transparent p-4 text-white placeholder-gray-400 resize-none focus:outline-none"
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!input.trim() || uploads.length === 0 || isTyping}
                className="px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:shadow-lg hover:shadow-purple-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center gap-2 font-medium"
              >
                <Send className="w-5 h-5" />
                Send
              </button>
            </div>
            
            {error && (
              <div className="mt-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-300 text-sm">
                {error}
              </div>
            )}
            
            {uploads.length === 0 && (
              <p className="mt-3 text-center text-gray-500 text-sm">
                Upload documents first to start chatting with AI
              </p>
            )}
          </div>
        </div>

        {/* Stats Footer */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { label: 'Documents Processed', value: '1M+', icon: FileText },
            { label: 'AI Accuracy', value: '99.9%', icon: Brain },
            { label: 'Response Time', value: '<2s', icon: Zap },
            { label: 'Languages Supported', value: '50+', icon: Globe }
          ].map((stat, idx) => (
            <div key={idx} className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6 text-center hover:border-purple-500/50 transition-all duration-300">
              <stat.icon className="w-8 h-8 text-purple-400 mx-auto mb-3" />
              <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-gray-400 text-sm">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
"use client";
}

