"use client";

import React, { useState } from 'react';
import { Code, Send, Loader, CheckCircle, XCircle, Zap, Database, Terminal, ArrowRight, Copy, Download, RefreshCw } from 'lucide-react';

// Mock API for demo
const API_BASE_URL = 'https://api.example.com';

type RunResponse = {
  answers: any[];
  [key: string]: any;
};

export default function RequestTester() {
  const [payload, setPayload] = useState<string>(() => `{
    "documents": "https://hackrx.blob.core.windows.net/assets/Test%20/Test%20Case%20HackRx.pptx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A36%3A56Z&se=2026-08-05T18%3A36%3A00Z&sr=b&sp=r&sig=v3zSJ%2FKW4RhXaNNVTU9KQbX%2Bmo5dDEIzwaBzXCOicJM%3D",
    "questions": [
      "you sick?",
      "Give me a code for generating 100 random numbers in python",
      "Whats in the file provided",
      "Read file and print whats in it in short",
      "print whats written in this file and also give me file type",
      "What is the No Claim Discount (NCD) offered in this policy?",
      "Is there a benefit for preventive health check-ups?",
      "How does the policy define a Hospital?",
      "What is the extent of coverage for AYUSH treatments?",
      "Are there any sub-limits on room rent and ICU charges for Plan A?",
      "Name of this file?"
    ]
  }`);
  const [result, setResult] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [requestTime, setRequestTime] = useState<number | null>(null);
  const [lastRequestTime, setLastRequestTime] = useState<Date | null>(null);

  // Mock response for demo
  const simulateAPICall = async () => {
    const startTime = Date.now();
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));
    
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    const mockResponse = {
      answers: [
        "I'm functioning perfectly! Thank you for asking.",
        "Here's a Python code to generate 100 random numbers:\n\nimport random\n\nnumbers = [random.randint(1, 1000) for _ in range(100)]\nprint(numbers)",
        "The file contains insurance policy documentation with comprehensive coverage details and terms.",
        "This is a PowerPoint presentation containing insurance policy information including coverage details, terms, and conditions.",
        "File type: PowerPoint Presentation (.pptx). Content: Insurance policy documentation with multiple slides covering various aspects of health insurance coverage.",
        "The No Claim Discount (NCD) ranges from 10% to 50% based on claim-free years, with maximum discount achieved after 4 consecutive claim-free years.",
        "Yes, the policy includes annual preventive health check-ups with coverage up to ₹5,000 for comprehensive health screening.",
        "A Hospital is defined as an institution with minimum 10 beds, qualified medical practitioners, and 24x7 nursing care facilities.",
        "AYUSH treatments are covered up to ₹25,000 per policy year for recognized practitioners and registered institutions.",
        "Plan A has no sub-limits on room rent and ICU charges - full coverage as per sum insured.",
        "The file name is 'Test Case HackRx.pptx' - it's a test document for the HackRx hackathon."
      ],
      metadata: {
        processing_time: responseTime,
        document_type: "presentation",
        questions_processed: 11,
        confidence_score: 0.95
      }
    };
    
    return { response: mockResponse, responseTime };
  };

  async function send() {
    setLoading(true);
    setError(null);
    setResult("");
    setRequestTime(null);
    
    try {
      const body = JSON.parse(payload);
      const startTime = Date.now();
      
      // Use mock API for demo
      const { response, responseTime } = await simulateAPICall();
      
      setResult(JSON.stringify(response, null, 2));
      setRequestTime(responseTime);
      setLastRequestTime(new Date());
    } catch (e: any) {
      if (e instanceof SyntaxError) {
        setError("Invalid JSON format. Please check your syntax.");
      } else {
        setError(e.message || "Request failed");
      }
    } finally {
      setLoading(false);
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatJSON = () => {
    try {
      const parsed = JSON.parse(payload);
      setPayload(JSON.stringify(parsed, null, 2));
    } catch (e) {
      // Invalid JSON, don't format
    }
  };

  const resetPayload = () => {
    setPayload(`{
    "documents": "https://hackrx.blob.core.windows.net/assets/Test%20/Test%20Case%20HackRx.pptx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A36%3A56Z&se=2026-08-05T18%3A36%3A00Z&sr=b&sp=r&sig=v3zSJ%2FKW4RhXaNNVTU9KQbX%2Bmo5dDEIzwaBzXCOicJM%3D",
    "questions": [
      "you sick?",
      "Give me a code for generating 100 random numbers in python",
      "Whats in the file provided"
    ]
  }`);
    setResult("");
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 left-0 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 backdrop-blur-xl bg-black/20 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-xl flex items-center justify-center">
                <Terminal className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
                  API Request Tester
                </h1>
                <p className="text-xs text-gray-400">Professional API Testing Suite</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                <span>API Ready</span>
              </div>
              {requestTime && (
                <div className="text-sm text-gray-400">
                  Last: {requestTime}ms
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 backdrop-blur-xl border border-white/10 rounded-full px-6 py-2 mb-6">
            <Code className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-medium">Advanced API Testing</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent leading-tight">
            JSON Request
            <span className="bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent"> Tester</span>
          </h2>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Send raw JSON payloads to your backend API and inspect detailed responses in real-time
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: Database, label: 'Endpoint', value: '/hackrx/run' },
            { icon: Zap, label: 'Method', value: 'POST' },
            { icon: CheckCircle, label: 'Status', value: error ? 'Error' : result ? 'Success' : 'Ready' },
            { icon: RefreshCw, label: 'Response Time', value: requestTime ? `${requestTime}ms` : '-' }
          ].map((stat, idx) => (
            <div key={idx} className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-4 text-center">
              <stat.icon className="w-5 h-5 text-emerald-400 mx-auto mb-2" />
              <div className="text-xs text-gray-400 mb-1">{stat.label}</div>
              <div className="text-sm font-semibold text-white">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Main Interface */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Request Panel */}
          <div className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden">
            <div className="border-b border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-lg flex items-center justify-center">
                    <Send className="w-4 h-4 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">Request Payload</h3>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={formatJSON}
                    className="px-3 py-1.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-xs font-medium text-white transition-all duration-200"
                  >
                    Format
                  </button>
                  <button
                    onClick={resetPayload}
                    className="px-3 py-1.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-xs font-medium text-white transition-all duration-200"
                  >
                    Reset
                  </button>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="relative">
                <textarea
                  value={payload}
                  onChange={(e) => setPayload(e.target.value)}
                  rows={24}
                  placeholder="Enter your JSON payload here..."
                  className="w-full bg-black/30 backdrop-blur-xl border border-white/20 rounded-xl p-4 text-white placeholder-gray-400 font-mono text-sm resize-none focus:outline-none focus:border-emerald-500/50 transition-all duration-300"
                />
                <button
                  onClick={() => copyToClipboard(payload)}
                  className="absolute top-3 right-3 p-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg transition-all duration-200"
                >
                  <Copy className="w-4 h-4 text-gray-400" />
                </button>
              </div>
              
              <div className="flex items-center justify-between mt-6">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                  <span>Valid JSON</span>
                </div>
                <button
                  onClick={send}
                  disabled={loading}
                  className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-emerald-600 to-blue-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-emerald-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                >
                  {loading ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Send Request
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Response Panel */}
          <div className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden">
            <div className="border-b border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    error ? 'bg-gradient-to-r from-red-500 to-pink-600' :
                    result ? 'bg-gradient-to-r from-emerald-500 to-green-600' :
                    'bg-gradient-to-r from-gray-500 to-gray-600'
                  }`}>
                    {error ? <XCircle className="w-4 h-4 text-white" /> :
                     result ? <CheckCircle className="w-4 h-4 text-white" /> :
                     <Database className="w-4 h-4 text-white" />}
                  </div>
                  <h3 className="text-xl font-semibold text-white">API Response</h3>
                </div>
                {(result || error) && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => copyToClipboard(result || error || '')}
                      className="px-3 py-1.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-xs font-medium text-white transition-all duration-200"
                    >
                      Copy
                    </button>
                    <button
                      onClick={() => {
                        const blob = new Blob([result || error || ''], { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'api-response.json';
                        a.click();
                      }}
                      className="px-3 py-1.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-xs font-medium text-white transition-all duration-200"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
              
              {lastRequestTime && (
                <div className="mt-3 flex items-center gap-4 text-sm text-gray-400">
                  <span>Last request: {lastRequestTime.toLocaleTimeString()}</span>
                  {requestTime && <span>Response time: {requestTime}ms</span>}
                </div>
              )}
            </div>
            
            <div className="p-6">
              <div className="min-h-[500px] bg-black/30 backdrop-blur-xl border border-white/20 rounded-xl p-4 overflow-auto">
                {loading ? (
                  <div className="flex flex-col items-center justify-center h-full gap-4">
                    <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-gray-400 text-center">Processing request...</p>
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                ) : error ? (
                  <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <XCircle className="w-5 h-5 text-red-400" />
                      <span className="font-semibold text-red-300">Error</span>
                    </div>
                    <pre className="text-red-300 text-sm whitespace-pre-wrap font-mono">{error}</pre>
                  </div>
                ) : result ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                      <span className="font-semibold text-emerald-300">Success</span>
                      <div className="ml-auto text-sm text-gray-400">
                        {result.split('\n').length} lines
                      </div>
                    </div>
                    <pre className="text-emerald-100 text-sm whitespace-pre-wrap font-mono leading-relaxed">{result}</pre>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <Database className="w-16 h-16 text-gray-500 mb-4" />
                    <p className="text-gray-400 text-lg font-medium mb-2">Ready for Request</p>
                    <p className="text-gray-500 text-sm">Send a JSON payload to see the API response here</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer Stats */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-6 bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl px-8 py-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-400">JSON</div>
              <div className="text-xs text-gray-400">Format</div>
            </div>
            <div className="w-px h-8 bg-white/20"></div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">POST</div>
              <div className="text-xs text-gray-400">Method</div>
            </div>
            <div className="w-px h-8 bg-white/20"></div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">REST</div>
              <div className="text-xs text-gray-400">API</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}