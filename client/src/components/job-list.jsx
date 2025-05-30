"use client";
import { useState, useEffect, useCallback } from "react";
import { useUser } from "@clerk/nextjs";
import { Bookmark, BookmarkCheck, Send, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/ui/avatar";
import JobDetailPanel from "@/components/job-detail-panel";

export default function JobList({ filters, onFiltersChange }) {
  const { user } = useUser();
  const [savedJobs, setSavedJobs] = useState([]);
  const [appliedJobs, setAppliedJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);

  const fetchJobs = useCallback(async (pageNum = 1, currentFilters = null, isNewSearch = false) => {
    if (!user?.id) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      let endpoint = `http://localhost:5000/api/recommended-jobs?userId=${user.id}&page=${pageNum}&limit=6`;
      
      const filtersToUse = currentFilters || filters;
      if (filtersToUse) {
        if (filtersToUse.skills && filtersToUse.skills.length > 0) {
          endpoint += `&skills=${encodeURIComponent(filtersToUse.skills.join(','))}`;
        }
        if (filtersToUse.remote) {
          endpoint += '&remote=true';
        }
        if (filtersToUse.salaryRange && (filtersToUse.salaryRange[0] > 50 || filtersToUse.salaryRange[1] < 150)) {
          endpoint += `&minSalary=${filtersToUse.salaryRange[0]}&maxSalary=${filtersToUse.salaryRange[1]}`;
        }
      }
      
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
      if (isNewSearch || pageNum === 1) {
        setJobs(data.jobs || []);
      } else {
        setJobs(prev => [...prev, ...(data.jobs || [])]);
      }
      
      setHasMore(data.hasMore || false);
      setPage(pageNum);
      
    } catch (error) {
      console.error('Error fetching recommended jobs:', error);
      setError(error.message);
      if (pageNum === 1) {
        setJobs([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, filters]);

  // Fetch user's saved and applied jobs
  const fetchUserJobStats = useCallback(async () => {
    if (!user?.id) return;
    
    try {
      const response = await fetch(`http://localhost:5000/api/user-job-actions?userId=${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setSavedJobs(data.saved || []);
        setAppliedJobs(data.applied || []);
      }
    } catch (error) {
      console.error('Error fetching user job actions:', error);
    }
  }, [user?.id]);

  // Initial load - separate useEffect to avoid dependency issues
  useEffect(() => {
    if (user?.id) {
      fetchJobs(1, filters, true);
    }
  }, [user?.id, fetchJobs]);

  // Load user job stats - separate useEffect
  useEffect(() => {
    if (user?.id) {
      fetchUserJobStats();
    }
  }, [user?.id, fetchUserJobStats]);

  useEffect(() => {
    if (user?.id && filters) {
      setPage(1);
      fetchJobs(1, filters, true);
    }
  }, [filters, user?.id, fetchJobs]);

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop !== document.documentElement.offsetHeight || isLoading || !hasMore) {
        return;
      }
      showMore();
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isLoading, hasMore]);

  const toggleSave = async (jobId, e) => {
    e.stopPropagation();
    
    try {
      const action = savedJobs.includes(jobId) ? 'unsave' : 'save';
      const response = await fetch('http://localhost:5000/api/job-action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
          jobId: jobId,
          action: action,
          type: 'saved'
        }),
      });
  
      if (response.ok) {
        setSavedJobs(prev =>
          action === 'save' 
            ? [...prev, jobId]
            : prev.filter(id => id !== jobId)
        );
        
        // Dispatch custom event to update stats
        console.log('Dispatching jobStatsUpdated event'); // Debug log
        const event = new CustomEvent('jobStatsUpdated');
        window.dispatchEvent(event);
      } else {
        console.error('Failed to save job:', response.status);
      }
    } catch (error) {
      console.error('Error toggling save:', error);
    }
  };
  
  const toggleApply = async (jobId, e) => {
    e.stopPropagation();
    
    try {
      const action = appliedJobs.includes(jobId) ? 'unapply' : 'apply';
      const response = await fetch('http://localhost:5000/api/job-action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
          jobId: jobId,
          action: action,
          type: 'applied'
        }),
      });
  
      if (response.ok) {
        setAppliedJobs(prev =>
          action === 'apply' 
            ? [...prev, jobId]
            : prev.filter(id => id !== jobId)
        );
        
        // Dispatch custom event to update stats
        console.log('Dispatching jobStatsUpdated event'); // Debug log
        const event = new CustomEvent('jobStatsUpdated');
        window.dispatchEvent(event);
      } else {
        console.error('Failed to apply to job:', response.status);
      }
    } catch (error) {
      console.error('Error toggling apply:', error);
    }
  };
  

  const showMore = () => {
    if (hasMore && !isLoading) {
      const nextPage = page + 1;
      fetchJobs(nextPage, filters, false);
    }
  };

  const handleJobClick = (job) => {
    setSelectedJob(job);
    setIsDetailOpen(true);
  };

  const closeJobDetail = () => {
    setIsDetailOpen(false);
  };

  if (error) {
    return (
      <div className="max-w-2xl w-full flex flex-col gap-4">
        <div className="text-center py-8">
          <p className="text-destructive text-sm mb-2">Error loading jobs</p>
          <p className="text-xs text-muted-foreground mb-4">{error}</p>
          <Button 
            variant="outline" 
            onClick={() => fetchJobs(1, filters, true)}
            className="text-xs"
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl w-full flex flex-col gap-4">
      {jobs.length === 0 && !isLoading && (
        <div className="text-xs text-muted-foreground py-8 text-center">
          No jobs match your resume profile or current filters. Try adjusting your criteria.
        </div>
      )}
      
      {jobs.map((job, index) => (
        <Card
          key={`${job.id}-${job.pinecone_id || ''}-${index}`}
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => handleJobClick(job)}
        >
          <CardHeader className="flex flex-row items-center gap-3 py-3 px-4">
            {job.logo && job.logo !== '/placeholder.svg?height=40&width=40' ? (
              <img 
                src={job.logo} 
                alt={job.company} 
                className="w-auto h-auto max-w-[28px] max-h-[28px] rounded-full object-cover border"
                style={{ aspectRatio: '1/1' }}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <Avatar 
              src="/placeholder.svg?height=40&width=40"
              alt={job.company} 
              size={28}
              style={{ display: job.logo && job.logo !== '/placeholder.svg?height=40&width=40' ? 'none' : 'flex' }}
            />
            <div className="flex flex-col">
              <span className="font-medium text-sm">{job.title}</span>
              <span className="text-xs text-muted-foreground">{job.company}</span>
              {job.experience && (
                <span className="text-xs text-muted-foreground">{job.experience}</span>
              )}
            </div>
            <div className="ml-auto flex items-center gap-2">
              <Badge className="text-xs px-2 py-0.5">{job.location}</Badge>
              {job.match_percentage && (
                <Badge variant="secondary" className="text-xs px-2 py-0.5 bg-green-100 text-green-800">
                  {job.match_percentage}% match
                </Badge>
              )}
              {job.rating && job.rating > 0 && (
                <Badge variant="outline" className="text-xs px-2 py-0.5">
                  ⭐ {job.rating}
                </Badge>
              )}
              
              {/* Apply Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => toggleApply(job.id, e)}
                aria-label={appliedJobs.includes(job.id) ? "Applied" : "Apply"}
                className={appliedJobs.includes(job.id) ? "text-green-600" : ""}
              >
                {appliedJobs.includes(job.id) ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>

              {/* Save Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => toggleSave(job.id, e)}
                aria-label={savedJobs.includes(job.id) ? "Unsave" : "Save"}
              >
                {savedJobs.includes(job.id) ? (
                  <BookmarkCheck className="w-4 h-4 text-primary" />
                ) : (
                  <Bookmark className="w-4 h-4" />
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="py-2 px-4">
            <div className="flex flex-wrap gap-2">
              {(job.tags || []).slice(0, 5).map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs px-2 py-0.5">
                  {tag}
                </Badge>
              ))}
              {job.tags && job.tags.length > 5 && (
                <Badge variant="outline" className="text-xs px-2 py-0.5">
                  +{job.tags.length - 5} more
                </Badge>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex justify-between text-xs text-muted-foreground px-4 py-2">
            <span>{job.salary}</span>
            <span>{job.posted}</span>
          </CardFooter>
        </Card>
      ))}
      
      {isLoading && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
        </div>
      )}
      
      {hasMore && !isLoading && jobs.length > 0 && (
        <Button variant="outline" className="self-center mt-2 text-xs" onClick={showMore}>
          Show More
        </Button>
      )}
      
      <JobDetailPanel
        job={selectedJob}
        isOpen={isDetailOpen}
        onClose={closeJobDetail}
      />
    </div>
  );
}
