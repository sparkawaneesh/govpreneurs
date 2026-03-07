import React from 'react';

interface ProposalLayoutProps {
  leftSidebar: React.ReactNode;
  children: React.ReactNode;
  rightSidebar: React.ReactNode;
}

export const ProposalLayout: React.FC<ProposalLayoutProps> = ({ 
  leftSidebar, 
  children, 
  rightSidebar 
}) => {
  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans">
      {/* Header could go here */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Opportunity Details */}
        <aside className="w-80 border-r bg-white overflow-y-auto hidden lg:block shadow-sm">
          {leftSidebar}
        </aside>

        {/* Center Panel - Editable Proposal */}
        <main className="flex-1 overflow-y-auto p-8 bg-slate-50">
          <div className="max-w-4xl mx-auto space-y-8 pb-20">
            {children}
          </div>
        </main>

        {/* Right Sidebar - AI Assistant */}
        <aside className="w-96 border-l bg-white overflow-y-auto hidden xl:block shadow-sm">
          {rightSidebar}
        </aside>
      </div>
    </div>
  );
};
