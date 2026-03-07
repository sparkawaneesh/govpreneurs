"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { ProposalLayout } from '@/components/proposal/ProposalLayout';
import { ProposalSection } from '@/components/proposal/ProposalSection';
import { OpportunitySidebar } from '@/components/proposal/OpportunitySidebar';
import { AIAssistantPanel } from '@/components/proposal/AIAssistantPanel';
import { Skeleton } from "@/components/ui/skeleton";

interface Section {
  title: string;
  content: string;
  citations?: { page: number }[];
}

interface ProposalData {
  opportunity_id: string;
  sections: Section[];
}

export default function ProposalReviewPage() {
  const params = useParams();
  const id = params.id as string;
  
  const [proposal, setProposal] = useState<ProposalData | null>(null);
  const [opportunity, setOpportunity] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Selection and Refinement state
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [isRefining, setIsRefining] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const mockOpp = {
          title: "Maintenance and Repair of HVAC Systems",
          agency: "U.S. General Services Administration (GSA)",
          solicitation_number: "GSA-2024-HVAC-001",
          posted_date: new Date().toISOString(),
          response_deadline: new Date(Date.now() + 86400000 * 30).toISOString(),
          naics_code: "238220",
          set_aside_type: "Small Business Set-Aside"
        };
        setOpportunity(mockOpp);

        const response = await fetch('http://localhost:8000/api/proposals/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            opportunity_id: id,
            company_id: "00000000-0000-4000-a000-000000000000"
          })
        });

        if (response.ok) {
          const data = await response.json();
          setProposal(data);
        }
      } catch (error) {
        console.error("Failed to fetch proposal:", error);
      } finally {
        setLoading(false);
      }
    }

    if (id) fetchData();
  }, [id]);

  const handleRefine = async (instruction: string) => {
    if (selectedIndex === null || !proposal) return;

    setIsRefining(true);
    const sectionToRefine = proposal.sections[selectedIndex];

    try {
      const response = await fetch('http://localhost:8000/api/proposals/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          section_text: sectionToRefine.content,
          instruction: instruction
        })
      });

      if (response.ok) {
        const data = await response.json();
        const updatedSections = [...proposal.sections];
        updatedSections[selectedIndex] = {
          ...sectionToRefine,
          content: data.updated_text
        };
        setProposal({ ...proposal, sections: updatedSections });
      }
    } catch (error) {
      console.error("Refinement failed:", error);
    } finally {
      setIsRefining(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="space-y-4 w-full max-w-2xl px-8">
          <Skeleton className="h-12 w-3/4" />
          <Skeleton className="h-[200px] w-full" />
          <Skeleton className="h-[200px] w-full" />
        </div>
      </div>
    );
  }

  return (
    <ProposalLayout
      leftSidebar={opportunity ? <OpportunitySidebar opportunity={opportunity} /> : <div />}
      rightSidebar={
        <AIAssistantPanel 
          selectedText={selectedIndex !== null ? proposal?.sections[selectedIndex].content : undefined}
          onRefine={handleRefine}
          isLoading={isRefining}
        />
      }
    >
      <div className="space-y-4 mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Proposal Draft
        </h1>
        <p className="text-sm text-slate-500 font-medium">
          Generated on {new Date().toLocaleDateString()} &bull; Tailored for {opportunity?.agency}
        </p>
      </div>

      {proposal?.sections.map((section, index) => (
        <ProposalSection 
          key={index} 
          title={section.title} 
          initialContent={section.content} 
          citations={section.citations}
          isSelected={selectedIndex === index}
          onSelect={() => setSelectedIndex(index)}
          onUpdate={(newText) => {
            const updatedSections = [...proposal.sections];
            updatedSections[index].content = newText;
            setProposal({ ...proposal, sections: updatedSections });
          }}
        />
      ))}
    </ProposalLayout>
  );
}
