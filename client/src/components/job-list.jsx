"use client"

import { useState } from "react";
import { Bookmark, BookmarkCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/ui/avatar";
import JobDetailPanel from "@/components/job-detail-panel";

// Sample job data
const ALL_JOBS = [
  {
    id: 1,
    title: "Senior Frontend Developer",
    company: "TechCorp",
    logo: "/placeholder.svg?height=40&width=40",
    location: "Remote",
    salary: "$120k - $150k",
    tags: ["React", "TypeScript", "Next.js"],
    relevancy: 95,
    posted: "2 days ago",
    description:
      "TechCorp is seeking a Senior Frontend Developer to join our growing team. You will be responsible for building user interfaces for our web applications using React and TypeScript.",
    responsibilities: [
      "Develop new user-facing features using React.js",
      "Build reusable components and libraries for future use",
      "Translate designs and wireframes into high-quality code",
      "Optimize components for maximum performance",
      "Collaborate with backend developers and designers",
    ],
    requirements: [
      "3+ years experience with React.js",
      "Strong proficiency in TypeScript",
      "Experience with Next.js and modern frontend tools",
      "Knowledge of responsive design principles",
      "Understanding of server-side rendering",
    ],
    benefits: [
      "Competitive salary",
      "Remote work options",
      "Health insurance",
      "401(k) matching",
      "Professional development budget",
    ],
    companyInfo:
      "TechCorp is a leading technology company specializing in web and mobile applications. We work with clients across various industries to deliver innovative solutions that drive business growth.",
  },
  {
    id: 2,
    title: "Full Stack Engineer",
    company: "InnovateLabs",
    logo: "/placeholder.svg?height=40&width=40",
    location: "San Francisco, CA",
    salary: "$130k - $160k",
    tags: ["Node.js", "React", "MongoDB"],
    relevancy: 88,
    posted: "1 day ago",
  },
  {
    id: 3,
    title: "UX/UI Designer",
    company: "DesignHub",
    logo: "/placeholder.svg?height=40&width=40",
    location: "New York, NY",
    salary: "$90k - $120k",
    tags: ["Figma", "UI Design", "User Research"],
    relevancy: 82,
    posted: "3 days ago",
  },
  {
    id: 4,
    title: "DevOps Engineer",
    company: "CloudSystems",
    logo: "/placeholder.svg?height=40&width=40",
    location: "Remote",
    salary: "$110k - $140k",
    tags: ["AWS", "Docker", "Kubernetes"],
    relevancy: 78,
    posted: "5 days ago",
  },
  {
    id: 5,
    title: "Product Manager",
    company: "ProductWave",
    logo: "/placeholder.svg?height=40&width=40",
    location: "London, UK",
    salary: "$100k - $130k",
    tags: ["Product Strategy", "Agile", "User Stories"],
    relevancy: 75,
    posted: "1 week ago",
  },
  {
    id: 6,
    title: "Data Scientist",
    company: "DataInsights",
    logo: "/placeholder.svg?height=40&width=40",
    location: "Berlin, Germany",
    salary: "$115k - $145k",
    tags: ["Python", "Machine Learning", "SQL"],
    relevancy: 72,
    posted: "1 week ago",
  },
  
];

export default function JobList() {
  const [savedJobs, setSavedJobs] = useState([]);
  const [visibleJobs, setVisibleJobs] = useState(4);
  const [selectedJob, setSelectedJob] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [filteredJobs, setFilteredJobs] = useState(ALL_JOBS);
  const [activeFilters, setActiveFilters] = useState(null);

  const toggleSave = (id, e) => {
    e.stopPropagation(); // Prevent card click when clicking save button
    setSavedJobs((prev) =>
      prev.includes(id) ? prev.filter((jobId) => jobId !== id) : [...prev, id]
    );
  };

  const showMore = () => {
    setVisibleJobs((prev) => Math.min(prev + 4, filteredJobs.length));
  };

  const handleJobClick = (job) => {
    setSelectedJob(job);
    setIsDetailOpen(true);
  };

  const closeJobDetail = () => {
    setIsDetailOpen(false);
  };

  const handleFiltersChange = (filters) => {
    setActiveFilters(filters);

    // Filter jobs based on selected criteria
    let jobs = [...ALL_JOBS];

    // Filter by skills/tags
    if (filters.skills.length > 0) {
      jobs = jobs.filter((job) =>
        filters.skills.some((skill) => job.tags.includes(skill))
      );
    }

    // Filter by salary range
    if (filters.salaryRange[0] > 50 || filters.salaryRange[1] < 150) {
      // For demo purposes, we'll just filter randomly
      jobs = jobs.filter(() => Math.random() > 0.2);
    }

    // Filter by remote
    if (filters.remote) {
      jobs = jobs.filter((job) => job.location.includes("Remote"));
    }

    setFilteredJobs(jobs);
    setVisibleJobs(4); // Reset visible jobs when filters change
  };

  return (
    <div className="space-y-4">
      {/* Job Detail Panel */}
      <JobDetailPanel job={selectedJob} isOpen={isDetailOpen} onClose={closeJobDetail} />

      {filteredJobs.slice(0, visibleJobs).map((job) => (
        <JobCard
          key={job.id}
          job={job}
          isSaved={savedJobs.includes(job.id)}
          onSave={(e) => toggleSave(job.id, e)}
          onClick={() => handleJobClick(job)}
        />
      ))}

      {visibleJobs < filteredJobs.length && (
        <Button variant="outline" className="w-full" onClick={showMore}>
          Show More
        </Button>
      )}

      {filteredJobs.length === 0 && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No jobs match your filters. Try adjusting your criteria.</p>
          <Button
            variant="outline"
            className="mt-4"
            onClick={() =>
              handleFiltersChange({
                salaryRange: [50, 150],
                skills: [],
                remote: false,
              })
            }
          >
            Reset Filters
          </Button>
        </div>
      )}
    </div>
  );
}

function JobCard({ job, isSaved, onSave, onClick }) {
  return (
    <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onClick}>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="flex items-center space-x-4">
          <Avatar className="h-10 w-10 rounded-md">
            <img src={job.logo || "/placeholder.svg"} alt={`${job.company} logo`} />
          </Avatar>
          <div>
            <h3 className="font-semibold">{job.title}</h3>
            <p className="text-sm text-muted-foreground">{job.company}</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onSave} className="h-8 w-8">
          {isSaved ? <BookmarkCheck className="h-5 w-5 text-primary" /> : <Bookmark className="h-5 w-5" />}
          <span className="sr-only">{isSaved ? "Unsave" : "Save"} job</span>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {job.location} • {job.salary}
            </div>
            <Badge variant="outline" className="bg-primary/10 text-primary">
              {job.relevancy}% Match
            </Badge>
          </div>
          <div className="flex flex-wrap gap-2 pt-2">
            {job.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
      <CardFooter className="border-t pt-4">
        <div className="flex w-full items-center justify-between">
          <span className="text-xs text-muted-foreground">Posted {job.posted}</span>
          <Button
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              // This would normally open the apply dialog
            }}
          >
            Apply Now
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}