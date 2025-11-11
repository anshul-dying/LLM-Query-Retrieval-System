"use client";

import React, { useRef, useState, useEffect } from 'react';
import { Upload, MessageSquare, FileText, Brain, Zap, Globe, Star, Send, Paperclip, Bot, User, ExternalLink, FileCheck, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Alert } from '@/components/ui/alert';
import { formatFileSize, formatTime } from '@/lib/utils';

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
  const [success, setSuccess] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Welcome to IntelliDocs AI! I'm your intelligent document assistant powered by advanced neural networks. Upload your documents and I'll provide contextual insights with unprecedented accuracy.",
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileDropRef = useRef<HTMLDivElement>(null);

  const features = [
    { icon: Brain, title: "AI-Powered Analysis", desc: "Advanced neural processing", color: "from-blue-500 to-purple-600" },
    { icon: Zap, title: "Lightning Fast", desc: "Sub-second response times", color: "from-yellow-500 to-orange-600" },
    { icon: Globe, title: "Multi-language", desc: "Support for 50+ languages", color: "from-green-500 to-teal-600" },
    { icon: Star, title: "Enterprise Grade", desc: "99.9% accuracy guarantee", color: "from-pink-500 to-rose-600" }
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

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (fileDropRef.current) {
      fileDropRef.current.classList.add('border-blue-500', 'bg-blue-500/10');
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (fileDropRef.current) {
      fileDropRef.current.classList.remove('border-blue-500', 'bg-blue-500/10');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (fileDropRef.current) {
      fileDropRef.current.classList.remove('border-blue-500', 'bg-blue-500/10');
    }
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload({ target: { files } } as any);
    }
  };

  const simulateUpload = async (files: File[]) => {
    setUploading(true);
    setError(null);
    setSuccess(null);
    
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
        setSuccess(`${file.name} uploaded successfully!`);
      } catch (err: any) {
        setError(`Failed to upload ${file.name}: ${err.message}`);
        break;
      }
    }
    
    setUploading(false);
  };

  const simulateAIResponse = async (question: string) => {
    setIsTyping(true);
    setError(null);
    
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
        references: references.length > 0 ? references : [],
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

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement> | { target: { files: File[] | null } }) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    
    const remainingSlots = 15 - uploads.length;
    const filesToUpload = files.slice(0, remainingSlots);
    
    if (files.length > remainingSlots) {
      setError(`Only ${remainingSlots} file slots remaining. Please remove some files first.`);
    }
    
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

  const removeFile = (index: number) => {
    setUploads(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 backdrop-blur-xl bg-black/20 border-b border-white/10" role="navigation" aria-label="Main navigation">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center" aria-hidden="true">
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
              <div className="flex items-center gap-2 text-sm text-gray-300" role="status" aria-live="polite">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" aria-hidden="true"></div>
                <span>AI Online</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6">
            <Alert variant="error" dismissible onDismiss={() => setError(null)}>
              {error}
            </Alert>
          </div>
        )}
        
        {success && (
          <div className="mb-6">
            <Alert variant="success" dismissible onDismiss={() => setSuccess(null)}>
              {success}
            </Alert>
          </div>
        )}

        {/* Hero Section */}
        <div className="text-center mb-8 sm:mb-12">
          <h2 className="text-3xl sm:text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent leading-tight">
            Transform Documents Into
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Intelligence</span>
          </h2>
          <p className="text-lg sm:text-xl text-gray-400 mb-8 max-w-3xl mx-auto px-4">
            Upload any document and unlock instant insights with our revolutionary AI-powered analysis engine
          </p>

          {/* Features Carousel */}
          <div className="flex justify-center mb-8">
            <Card className="min-w-[280px] sm:min-w-80">
              {features.map((feature, idx) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-4 transition-all duration-500 ${
                      idx === activeFeature ? 'opacity-100 transform translate-y-0' : 'opacity-0 absolute transform translate-y-4 pointer-events-none'
                    }`}
                    aria-hidden={idx !== activeFeature}
                  >
                    <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-xl flex items-center justify-center flex-shrink-0`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                      <p className="text-gray-400 text-sm">{feature.desc}</p>
                    </div>
                  </div>
                );
              })}
            </Card>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="mb-8">
          <Card hover glow className="p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
              <div className="flex items-center gap-3">
                <Upload className="w-6 h-6 text-blue-400 flex-shrink-0" aria-hidden="true" />
                <div>
                  <h3 className="text-xl font-semibold text-white">Document Upload</h3>
                  <p className="text-gray-400 text-sm">Drag & drop or click to upload up to 15 files</p>
                </div>
              </div>
              <div className="text-left sm:text-right text-sm text-gray-400">
                <div className="font-medium">{uploads.length}/15 files</div>
                <div className="w-full sm:w-32 h-2 bg-gray-700 rounded-full mt-1">
                  <div
                    className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
                    style={{ width: `${(uploads.length / 15) * 100}%` }}
                    role="progressbar"
                    aria-valuenow={uploads.length}
                    aria-valuemin={0}
                    aria-valuemax={15}
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
              accept=".pdf,.doc,.docx,.txt,.rtf,.pptx,.ppt,.xlsx,.xls"
              id="file-upload"
              aria-label="Upload documents"
            />

            <div
              ref={fileDropRef}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className="border-2 border-dashed border-gray-600 rounded-2xl p-8 sm:p-12 text-center hover:border-blue-500 transition-all duration-300 cursor-pointer group focus-within:ring-2 focus-within:ring-blue-500 focus-within:outline-none"
              role="button"
              tabIndex={0}
              aria-label="Click or drag to upload files"
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  fileInputRef.current?.click();
                }
              }}
            >
              {uploading ? (
                <div className="flex flex-col items-center gap-4">
                  <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" aria-label="Uploading files"></div>
                  <p className="text-gray-400">Processing files...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Paperclip className="w-8 h-8 text-blue-400" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-white mb-2">Click to upload documents</p>
                    <p className="text-gray-400 text-sm">PDF, DOC, DOCX, TXT, RTF, PPTX, XLSX supported</p>
                  </div>
                </div>
              )}
            </div>

            {/* Uploaded Files Grid */}
            {uploads.length > 0 && (
              <div className="mt-6 sm:mt-8">
                <h4 className="text-sm font-medium text-gray-300 mb-4">Uploaded Files ({uploads.length})</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {uploads.map((file, idx) => (
                    <Card key={idx} hover className="p-4 group relative">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileCheck className="w-5 h-5 text-green-400" aria-hidden="true" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-white truncate" title={file.filename}>
                            {file.filename}
                          </p>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className="text-xs text-gray-400">{formatFileSize(file.size)}</span>
                            <span className="text-xs text-gray-500">•</span>
                            <span className="text-xs text-gray-400">
                              {formatTime(file.uploadedAt)}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(idx)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded-lg"
                          aria-label={`Remove ${file.filename}`}
                        >
                          <X className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>

          {/* Chat Interface */}
        <Card className="overflow-hidden flex flex-col" style={{ height: '600px', display: 'flex' }}>
          <div className="border-b border-white/10 p-4 sm:p-6 flex-shrink-0">
            <div className="flex items-center gap-3 flex-wrap">
              <MessageSquare className="w-6 h-6 text-purple-400 flex-shrink-0" aria-hidden="true" />
              <h3 className="text-xl font-semibold text-white">AI Chat Assistant</h3>
              <div className="flex items-center gap-2 ml-auto">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" aria-hidden="true"></div>
                <span className="text-sm text-gray-400">Ready to help</span>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth bg-gradient-to-b from-transparent to-black/10" style={{ minHeight: 0 }} role="log" aria-live="polite" aria-label="Chat messages">
            {messages.map((message) => {
              const Icon = message.role === 'user' ? User : Bot;
              return (
                <div key={message.id} className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600'
                        : 'bg-gradient-to-r from-green-500 to-teal-600'
                    }`}
                    aria-label={message.role === 'user' ? 'User' : 'Assistant'}
                  >
                    <Icon className="w-5 h-5" aria-hidden="true" />
                  </div>
                  <div className={`flex-1 ${message.role === 'user' ? 'text-right' : ''}`}>
                    <div
                      className={`inline-block p-4 rounded-2xl max-w-full ${message.role === 'user' ? 'max-w-[85%] sm:max-w-[75%]' : 'max-w-full'} ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                          : 'bg-white/10 backdrop-blur-xl border border-white/20 text-white'
                      }`}
                    >
                      <div className="prose prose-invert max-w-none">
                        <p className="whitespace-pre-wrap leading-relaxed break-words text-sm sm:text-base">{message.content}</p>
                      </div>
                    </div>

                    {message.references && message.references.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs text-gray-400 mb-2 font-medium flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          References ({message.references.length}):
                        </p>
                        <div className="grid grid-cols-1 gap-2">
                          {message.references.map((ref, idx) => (
                            <div
                              key={idx}
                              className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 text-sm bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-3 hover:bg-white/10 hover:border-blue-500/30 transition-all"
                            >
                              <div className="flex items-center gap-2 flex-1 min-w-0">
                                <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" aria-hidden="true" />
                                <span className="text-gray-300 truncate font-medium" title={ref.doc_name || 'Document'}>
                                  {ref.doc_name || 'Document'}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 text-xs flex-wrap flex-shrink-0">
                                {ref.page && (
                                  <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded font-medium">Page {ref.page}</span>
                                )}
                                {ref.clause && (
                                  <span className="text-gray-400 truncate max-w-[200px] sm:max-w-[250px]" title={ref.clause}>
                                    {ref.clause}
                                  </span>
                                )}
                              </div>
                              {ref.doc_url && (
                                <a
                                  href={ref.doc_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-400 hover:text-blue-300 transition-colors flex-shrink-0 p-1 hover:bg-blue-500/20 rounded"
                                  aria-label={`Open ${ref.doc_name || 'document'} in new tab`}
                                >
                                  <ExternalLink className="w-4 h-4" aria-hidden="true" />
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className={`mt-2 text-xs text-gray-500 ${message.role === 'user' ? 'text-right' : ''}`}>
                      <time dateTime={message.timestamp.toISOString()}>
                        {message.timestamp.toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit'
                        })}
                      </time>
                    </div>
                  </div>
                </div>
              );
            })}

            {isTyping && (
              <div className="flex gap-4" aria-label="AI is typing">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-xl flex items-center justify-center">
                  <Bot className="w-5 h-5" aria-hidden="true" />
                </div>
                <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} aria-hidden="true" />
          </div>

          {/* Input */}
          <div className="border-t border-white/10 p-4 sm:p-6 flex-shrink-0">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask me anything about your documents... (Press Enter to send, Shift+Enter for new line)"
                  className="min-h-[80px] sm:min-h-[100px]"
                  aria-label="Chat input"
                />
              </div>
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || uploads.length === 0 || isTyping}
                isLoading={isTyping}
                className="h-auto px-6 py-3 flex-shrink-0"
                aria-label="Send message"
              >
                <Send className="w-5 h-5" aria-hidden="true" />
                <span className="hidden sm:inline ml-2">Send</span>
              </Button>
            </div>

            {uploads.length === 0 && (
              <p className="mt-3 text-center text-gray-500 text-sm" role="alert">
                Upload documents first to start chatting with AI
              </p>
            )}
          </div>
        </Card>

        {/* Stats Footer */}
        <div className="mt-8 sm:mt-12 grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {[
            { label: 'Documents Processed', value: '1M+', icon: FileText },
            { label: 'AI Accuracy', value: '99.9%', icon: Brain },
            { label: 'Response Time', value: '<2s', icon: Zap },
            { label: 'Languages Supported', value: '50+', icon: Globe }
          ].map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <Card key={idx} hover className="p-6 text-center">
                <Icon className="w-8 h-8 text-purple-400 mx-auto mb-3" aria-hidden="true" />
                <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-gray-400 text-sm">{stat.label}</div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
