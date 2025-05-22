"use client"
import { X, Briefcase, MapPin, Calendar, DollarSign, Clock, Building, CheckCircle, ExternalLink, Target, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Avatar } from "@/components/ui/avatar"

export default function JobDetailPanel({ job, isOpen, onClose }) {
  if (!job) return null

  const handleApplyNow = () => {
    if (job.job_url) {
      window.open(job.job_url, '_blank');
    }
  };

  return (
    <>
      {/* Backdrop overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
        />
      )}
      
      {/* Right-side sliding panel */}
      <div className={`fixed top-0 right-0 h-full w-full max-w-2xl bg-background border-l shadow-lg z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-start gap-4 p-6 border-b">
            {/* Display company logo with max height constraint */}
            {job.logo && job.logo !== '/placeholder.svg?height=60&width=60' ? (
              <img 
                src={job.logo} 
                alt={job.company} 
                className="w-auto h-auto max-w-[60px] max-h-[60px] rounded-full object-cover border-2"
                style={{ aspectRatio: '1/1' }}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <Avatar 
              src="/placeholder.svg?height=60&width=60"
              alt={job.company} 
              size={60}
              style={{ display: job.logo && job.logo !== '/placeholder.svg?height=60&width=60' ? 'none' : 'flex' }}
            />
            <div className="flex-1">
              <h2 className="text-xl font-bold">{job.title}</h2>
              <div className="flex items-center gap-2 mt-2">
                <Building className="w-4 h-4 text-muted-foreground" />
                <span className="text-lg font-semibold">{job.company}</span>
                {job.rating && job.rating > 0 && (
                  <div className="flex items-center gap-1 ml-2">
                    <Star className="w-4 h-4 text-yellow-500 fill-current" />
                    <span className="text-sm font-medium">{job.rating}</span>
                    {job.review_count && job.review_count > 0 && (
                      <span className="text-xs text-muted-foreground">({job.review_count} reviews)</span>
                    )}
                  </div>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  <span>{job.location}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Briefcase className="w-4 h-4" />
                  <span>Full-time</span>
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  <span>{job.salary}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>{job.posted}</span>
                </div>
                {job.experience && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{job.experience}</span>
                  </div>
                )}
                {job.match_percentage && (
                  <div className="flex items-center gap-1">
                    <Target className="w-4 h-4 text-green-600" />
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {job.match_percentage}% match
                    </Badge>
                  </div>
                )}
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Scrollable content */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-6">
              {job.tags && job.tags.length > 0 && (
                <>
                  <div>
                    <h3 className="font-semibold mb-2">Required Skills & Keywords</h3>
                    <div className="flex flex-wrap gap-2">
                      {job.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-sm">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <Separator />
                </>
              )}

              <div>
                <h3 className="font-semibold mb-2">Job Description</h3>
                <div className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {job.description}
                </div>
              </div>

              <Separator />

              {job.experience && (
                <>
                  <div>
                    <h3 className="font-semibold mb-2">Experience Required</h3>
                    <p className="text-sm text-muted-foreground">{job.experience}</p>
                  </div>
                  <Separator />
                </>
              )}

              {job.locations_array && job.locations_array.length > 0 && (
                <>
                  <div>
                    <h3 className="font-semibold mb-2">Available Locations</h3>
                    <div className="flex flex-wrap gap-2">
                      {job.locations_array.map((location, index) => (
                        <Badge key={index} variant="secondary" className="text-sm">
                          {location}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <Separator />
                </>
              )}

              <div>
                <h3 className="font-semibold mb-2">About {job.company}</h3>
                <div className="text-sm text-muted-foreground leading-relaxed">
                  <p>{job.companyInfo}</p>
                  {job.rating && job.rating > 0 && job.review_count && job.review_count > 0 && (
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        <span className="font-medium">{job.rating}</span>
                      </div>
                      <span className="text-xs">Based on {job.review_count} employee reviews</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t p-6">
            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose} className="flex-1">
                Close
              </Button>
              {job.job_url && (
                <Button className="flex items-center gap-2 flex-1" onClick={handleApplyNow}>
                  <ExternalLink className="w-4 h-4" />
                  Apply Now
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
