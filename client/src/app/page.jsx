"use client"
import "../styles/globals.css";
import JobList from "@/components/job-list"
import StatsBox from "@/components/stats-box"
import ChatBot from "@/components/chat-bot"
import { SidebarProvider, SidebarInset, SidebarContent } from "@/components/ui/sidebar"
import JobSidebar from "@/components/job-sidebar"
import FloatingHeader from "@/components/floating-header"
import JobFilters from "@/components/job-filters"

export default function JobDashboard() {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen bg-background" style={{ postition: "fixed", top: 0, left: 0, right: 0}}>
        <SidebarInset>
          <JobSidebar />
        </SidebarInset>
        <SidebarContent>
          <FloatingHeader />
          <div className="container flex-1 grid gap-4 md:grid-cols-[1fr_350px] lg:grid-cols-[1fr_400px] p-4 pt-20 sm:p-6 sm:pt-24">
            <main className="flex flex-col gap-4">
              <h1 className="text-2xl font-semibold tracking-tight">Suggested Jobs</h1>
              <JobFilters onFiltersChange={(filters) => {}} />
              <JobList />
            </main>
            <aside className="flex flex-col gap-4">
              <StatsBox />
              <ChatBot />
            </aside>
          </div>
        </SidebarContent>
      </div>
    </SidebarProvider>
  )
}
