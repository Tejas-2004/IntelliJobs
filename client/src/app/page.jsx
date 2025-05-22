"use client"
import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import io from "socket.io-client";
import "../styles/globals.css";
import JobList from "@/components/job-list";
import StatsBox from "@/components/stats-box";
import ChatBot from "@/components/chat-bot";
import { SidebarProvider, SidebarInset, SidebarContent } from "@/components/ui/sidebar";
import JobSidebar from "@/components/job-sidebar";
import FloatingHeader from "@/components/floating-header";
import JobFilters from "@/components/job-filters";
import UploadResume from "@/components/upload-resume";

export default function JobDashboard() {
  const { user, isLoaded } = useUser();
  const [hasResume, setHasResume] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [socket, setSocket] = useState(null);

  // Initialize WebSocket connection
  useEffect(() => {
    if (isLoaded && user?.id) {
      const newSocket = io("http://localhost:5000/resume");
      newSocket.on("resume_processed", (data) => {
        if (data.userId === user.id) {
          if (data.success) {
            setHasResume(true);
          } else {
            console.error("Resume processing failed:", data.error);
          }
        }
      });
      setSocket(newSocket);
      checkUserResume(user.id);
      return () => {
        newSocket.disconnect();
      };
    }
  }, [user, isLoaded]);

  const checkUserResume = async (userId) => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/api/check-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId }),
      });
      if (!response.ok) throw new Error('Failed to check resume status');
      const data = await response.json();
      setHasResume(data.hasResume);
    } catch (error) {
      console.error('Error checking resume status:', error);
      setHasResume(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen bg-background">
        <SidebarInset>
          <JobSidebar />
        </SidebarInset>
        <SidebarContent>
          <FloatingHeader />
          <div className="container flex-1 grid gap-4 md:grid-cols-[1fr_350px] lg:grid-cols-[1fr_400px] p-4 pt-20 sm:p-6 sm:pt-24">
            {/* LEFT COLUMN */}
            <main className="flex flex-col gap-4" >
              {isLoading ? (
                <div className="flex items-center justify-center p-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
              ) : hasResume ? (
                <>
                  <h1 className="text-2xl font-semibold tracking-tight">Suggested Jobs</h1>
                  <JobFilters onFiltersChange={(filters) => {}} />
                  <JobList />
                </>
              ) : (
                <UploadResume />
              )}
            </main>
            {/* RIGHT COLUMN */}
            <aside className="flex flex-col gap-4 ml-8">
              {hasResume && (
                <div className="sticky top-24 flex flex-col gap-4">
                  <StatsBox />
                  <ChatBot />
                </div>
            )}
            </aside>
          </div>
        </SidebarContent>
      </div>
    </SidebarProvider>
  );
}
