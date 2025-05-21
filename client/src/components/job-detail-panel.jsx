"use client"

import { X, Briefcase, MapPin, Calendar, DollarSign, Clock, Building, CheckCircle, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Avatar } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from "@/components/ui/dialog"

export default function JobDetailPanel({ job, isOpen, onClose }) {
  if (!job) return null

  return (
    <div
      className={cn(
        "fixed top-0 right-0 z-30 h-screen w-full max-w-md bg-background border-l shadow-lg transform transition-transform duration-300 overflow-y-auto",
        isOpen ? "translate-x-0" : "translate-x-full",
      )}
    >
      <div className="sticky top-0 z-10 flex items-center justify-between p-4 bg-background/80 backdrop-blur-md border-b">
        <h2 className="text-xl font-semibold truncate">{job.title}</h2>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start gap-4">
          <Avatar className="h-16 w-16 rounded-md">
            <img src={job.logo || "/placeholder.svg"} alt={`${job.company} logo`} />
          </Avatar>
          <div className="space-y-1">
            <h3 className="text-xl font-semibold">{job.title}</h3>
            <p className="text-muted-foreground">{job.company}</p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin className="h-4 w-4" />
              <span>{job.location}</span>
            </div>
          </div>
        </div>

        {/* Relevancy and Apply */}
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="bg-primary/10 text-primary px-3 py-1">
            {job.relevancy}% Match
          </Badge>

          <Dialog>
            <DialogTrigger asChild>
              <Button>Apply Now</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Apply for {job.title}</DialogTitle>
              </DialogHeader>
              <div className="py-4">
                <p>
                  You're about to apply for the {job.title} position at {job.company}.
                </p>
                <p className="mt-2">Your profile and resume will be sent to the employer.</p>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Confirm Application</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Job Details */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1 p-3 border rounded-md">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Briefcase className="h-4 w-4" />
              <span>Job Type</span>
            </div>
            <p className="font-medium">Full-time</p>
          </div>

          <div className="flex flex-col gap-1 p-3 border rounded-md">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <DollarSign className="h-4 w-4" />
              <span>Salary</span>
            </div>
            <p className="font-medium">{job.salary}</p>
          </div>

          <div className="flex flex-col gap-1 p-3 border rounded-md">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>Posted</span>
            </div>
            <p className="font-medium">{job.posted}</p>
          </div>

          <div className="flex flex-col gap-1 p-3 border rounded-md">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>Experience</span>
            </div>
            <p className="font-medium">3+ years</p>
          </div>
        </div>

        {/* Skills */}
        <div>
          <h4 className="font-medium mb-2">Required Skills</h4>
          <div className="flex flex-wrap gap-2">
            {job.tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Description */}
        <div>
          <h4 className="font-medium mb-2">Job Description</h4>
          <p className="text-sm text-muted-foreground">
            {job.description ||
              `We are looking for a talented ${job.title} to join our team at ${job.company}. 
            This is an exciting opportunity to work on cutting-edge projects in a collaborative environment.
            The ideal candidate will have experience with ${job.tags.join(", ")} and a passion for creating 
            exceptional user experiences.`}
          </p>
        </div>

        <Separator />

        {/* Responsibilities */}
        <div>
          <h4 className="font-medium mb-2">Responsibilities</h4>
          <ul className="space-y-2">
            {(
              job.responsibilities || [
                "Design and implement new features and functionality",
                "Write clean, maintainable, and efficient code",
                "Collaborate with cross-functional teams",
                "Participate in code reviews and technical discussions",
                "Troubleshoot and debug issues",
              ]
            ).map((item, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Requirements */}
        <div>
          <h4 className="font-medium mb-2">Requirements</h4>
          <ul className="space-y-2">
            {(
              job.requirements || [
                `${job.tags[0]} experience (3+ years)`,
                `Proficiency with ${job.tags.slice(1, 3).join(" and ")}`,
                "Strong problem-solving skills",
                "Excellent communication skills",
                "Bachelor's degree in Computer Science or related field",
              ]
            ).map((item, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <Separator />

        {/* Company Info */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Building className="h-5 w-5" />
            <h4 className="font-medium">About {job.company}</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            {job.companyInfo ||
              `${job.company} is a leading company in the tech industry, 
            focused on delivering innovative solutions to complex problems. 
            With a team of talented professionals, we strive to create products 
            that make a difference in people's lives.`}
          </p>
          <Button variant="outline" className="mt-4 w-full gap-2">
            <ExternalLink className="h-4 w-4" />
            Visit Company Website
          </Button>
        </div>
      </div>
    </div>
  )
}
