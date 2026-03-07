import React from 'react';
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface OpportunitySidebarProps {
  opportunity: {
    title: string;
    agency: string;
    solicitation_number: string;
    posted_date: string;
    response_deadline: string;
    naics_code: string;
    set_aside_type: string;
  };
}

export const OpportunitySidebar: React.FC<OpportunitySidebarProps> = ({ opportunity }) => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Opportunity</h2>
        <p className="text-sm text-slate-600 leading-snug font-medium">{opportunity.title}</p>
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <label className="text-xs uppercase font-bold text-slate-400 tracking-wider">Agency</label>
          <p className="text-sm font-semibold text-slate-700">{opportunity.agency}</p>
        </div>

        <div>
          <label className="text-xs uppercase font-bold text-slate-400 tracking-wider">Solicitation #</label>
          <p className="text-sm font-mono font-medium text-slate-600">{opportunity.solicitation_number}</p>
        </div>

        <div className="flex gap-2 flex-wrap">
          <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-100">{opportunity.naics_code}</Badge>
          <Badge variant="outline" className="text-slate-600 border-slate-200">{opportunity.set_aside_type}</Badge>
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <label className="text-xs uppercase font-bold text-slate-400 tracking-wider">Posted Date</label>
          <p className="text-sm text-slate-700">{new Date(opportunity.posted_date).toLocaleDateString()}</p>
        </div>

        <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
          <label className="text-xs uppercase font-bold text-amber-700 tracking-wider">Response Deadline</label>
          <p className="text-sm font-bold text-amber-900">{new Date(opportunity.response_deadline).toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
};
