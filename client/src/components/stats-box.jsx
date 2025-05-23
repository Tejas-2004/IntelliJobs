"use client";

import { Briefcase, CheckCircle, Bookmark } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState, useEffect, useCallback, useRef } from "react";
import { useUser } from "@clerk/nextjs";

export default function StatsBox() {
  const { user } = useUser();
  const [stats, setStats] = useState({
    saved: 0,
    applied: 0
  });

  const fetchJobStats = useCallback(async () => {
    if (!user?.id) return;

    try {
      const response = await fetch(`http://localhost:5000/api/job-stats?userId=${user.id}`);
      if (response.ok) {
        const data = await response.json();
        console.log('Stats fetched:', data);
        setStats(data);
      } else {
        console.error('Failed to fetch stats:', response.status);
      }
    } catch (error) {
      console.error('Error fetching job stats:', error);
    }
  }, [user?.id]);

  // Use ref to store the latest fetchJobStats function
  const fetchJobStatsRef = useRef(fetchJobStats);
  fetchJobStatsRef.current = fetchJobStats;

  // Initial load
  useEffect(() => {
    if (user?.id) {
      fetchJobStats();
    }
  }, [user?.id, fetchJobStats]);

  // Listen for custom events to refresh stats
  useEffect(() => {
    const handleStatsUpdate = (event) => {
      console.log('Stats update event received', event.detail);
      // Use ref to avoid stale closure
      setTimeout(() => {
        fetchJobStatsRef.current();
      }, 300);
    };

    // Add event listener
    window.addEventListener('jobStatsUpdated', handleStatsUpdate);

    // Cleanup
    return () => {
      window.removeEventListener('jobStatsUpdated', handleStatsUpdate);
    };
  }, []); // Empty dependency array to avoid stale closure

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Saved Jobs</CardTitle>
          <Bookmark className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.saved}</div>
          <p className="text-xs text-muted-foreground">
            Jobs saved for later
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Applied Jobs</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.applied}</div>
          <p className="text-xs text-muted-foreground">
            Applications submitted
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
