"use client";

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles, MessageSquare, History, Wand2, Loader2 } from "lucide-react";

interface AIAssistantPanelProps {
  selectedText?: string;
  onRefine: (instruction: string) => void;
  isLoading: boolean;
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({ 
  selectedText, 
  onRefine, 
  isLoading 
}) => {
  const [instruction, setInstruction] = useState("");

  const handleRefineClick = () => {
    if (instruction && selectedText) {
      onRefine(instruction);
      setInstruction("");
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="p-6 border-b bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5" />
          <h2 className="text-lg font-bold">Proposal AI Assistant</h2>
        </div>
        <p className="text-xs text-blue-100">Refine your proposal with intelligent edits.</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {selectedText ? (
          <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-lg">
            <label className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">Selected Section</label>
            <p className="text-xs text-indigo-900 line-clamp-3 mt-1 italic">"{selectedText}"</p>
          </div>
        ) : (
          <div className="flex items-center justify-center h-24 bg-slate-50 border border-dashed border-slate-200 rounded-xl">
            <p className="text-xs text-slate-400 font-medium">Select a section to refine it.</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" size="sm" className="text-xs gap-1 border-indigo-100 text-indigo-700 h-10 hover:bg-indigo-50">
            <Wand2 className="w-3.5 h-3.5" /> Tone Check
          </Button>
          <Button variant="outline" size="sm" className="text-xs gap-1 border-indigo-100 text-indigo-700 h-10 hover:bg-indigo-50">
            <History className="w-3.5 h-3.5" /> Version Hist
          </Button>
        </div>
      </div>

      <div className="p-4 border-t bg-slate-50">
        <div className="flex gap-2">
          <Input 
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            disabled={!selectedText || isLoading}
            placeholder={selectedText ? "How should I refine this?" : "Select a section first..."} 
            className="text-sm shadow-inner placeholder:text-slate-400 border-slate-200 focus-visible:ring-indigo-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleRefineClick();
            }}
          />
          <Button 
            onClick={handleRefineClick}
            disabled={!selectedText || !instruction || isLoading}
            size="icon" 
            className="bg-indigo-600 hover:bg-indigo-700 shrink-0 shadow-sm shadow-indigo-200"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-white" />}
          </Button>
        </div>
        <p className="text-[10px] text-slate-400 mt-2 text-center">
          Powered by GovPreneurs AI.
        </p>
      </div>
    </div>
  );
};
