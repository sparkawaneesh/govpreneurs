"use client";

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

interface ProposalSectionProps {
  title: string;
  initialContent: string;
  citations?: { page: number }[];
  isSelected?: boolean;
  onSelect?: () => void;
  onUpdate?: (content: string) => void;
}

export const ProposalSection: React.FC<ProposalSectionProps> = ({ 
  title, 
  initialContent,
  citations,
  isSelected,
  onSelect,
  onUpdate 
}) => {
  const [content, setContent] = useState(initialContent);

  // Update internal state if initialContent changes (e.g. after refinement)
  React.useEffect(() => {
    setContent(initialContent);
  }, [initialContent]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    if (onUpdate) onUpdate(newContent);
  };

  return (
    <Card 
      onClick={onSelect}
      className={cn(
        "shadow-md hover:shadow-lg transition-all duration-200 border-none cursor-pointer ring-1",
        isSelected ? "ring-2 ring-indigo-500 shadow-indigo-100" : "ring-slate-200"
      )}
    >
      <CardHeader className="bg-slate-50/50 border-b border-slate-100 rounded-t-lg">
        <CardTitle className="text-lg font-semibold text-slate-800 tracking-tight">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <Textarea 
          value={content}
          onChange={handleChange}
          className="min-h-[200px] border-none focus-visible:ring-0 text-slate-700 leading-relaxed p-0 resize-none overflow-hidden"
          placeholder="Enter section content..."
        />
      </CardContent>
      {citations && citations.length > 0 && (
        <CardFooter className="flex flex-col items-start gap-2 pt-0 pb-6 border-t border-slate-50 mt-4">
          <label className="text-[10px] uppercase font-bold text-slate-400 tracking-widest pt-4">Sources</label>
          <div className="flex gap-2 flex-wrap">
            {citations.map((cite, idx) => (
              <Badge key={idx} variant="secondary" className="bg-slate-100 text-slate-600 border-slate-200 text-[10px] hover:bg-slate-200 transition-colors">
                RFP Page {cite.page}
              </Badge>
            ))}
          </div>
        </CardFooter>
      )}
    </Card>
  );
};
