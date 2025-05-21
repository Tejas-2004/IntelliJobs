"use client"

import { useState } from "react"
import { Filter, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, SheetFooter } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"

export default function JobFilters({ onFiltersChange }) {
  const [filters, setFilters] = useState({
    // jobTypes: [],
    // locations: [],
    // experienceLevels: [],
    salaryRange: [50, 150],
    skills: [],
    remote: false,
  })

  const [activeFiltersCount, setActiveFiltersCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)

  // const jobTypes = ["Full-time", "Part-time", "Contract", "Freelance", "Internship"]
  // const locations = ["Remote", "San Francisco", "New York", "London", "Berlin", "Toronto"]
  // const experienceLevels = ["Entry Level", "Mid Level", "Senior", "Lead", "Manager", "Director"]
  const skillsList = ["JavaScript", "React", "TypeScript", "Node.js", "Python", "AWS", "Docker", "UI/UX", "Figma"]

  const updateFilters = (key, value) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)

    // Count active filters
    let count = 0
    // if (newFilters.jobTypes.length) count++
    // if (newFilters.locations.length) count++
    // if (newFilters.experienceLevels.length) count++
    if (newFilters.skills.length) count++
    if (newFilters.remote) count++
    if (newFilters.salaryRange[0] > 50 || newFilters.salaryRange[1] < 150) count++

    setActiveFiltersCount(count)
  }

  const toggleArrayItem = (key, item) => {
    const array = filters[key]
    const newArray = array.includes(item) ? array.filter((i) => i !== item) : [...array, item]

    updateFilters(key, newArray)
  }

  const resetFilters = () => {
    setFilters({
      // jobTypes: [],
      // locations: [],
      // experienceLevels: [],
      salaryRange: [50, 150],
      skills: [],
      remote: false,
    })
    setActiveFiltersCount(0)
    onFiltersChange({
      // jobTypes: [],
      // locations: [],
      // experienceLevels: [],
      salaryRange: [50, 150],
      skills: [],
      remote: false,
    })
  }

  const applyFilters = () => {
    onFiltersChange(filters)
    setIsOpen(false)
  }

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Job Filters</h2>
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" className="gap-2">
              <Filter className="h-4 w-4" />
              Filters
              {activeFiltersCount > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {activeFiltersCount}
                </Badge>
              )}
            </Button>
          </SheetTrigger>
          <SheetContent className="w-full sm:max-w-md overflow-y-auto">
            <SheetHeader>
              <SheetTitle>Filter Jobs</SheetTitle>
            </SheetHeader>

            <div className="py-4 space-y-6 px-4">
              {/* Job Type */}
              {/* <div className="space-y-2"> */}
                {/* <h3 className="font-medium">Job Type</h3> */}
                {/* <div className="grid grid-cols-2 gap-2"> */}
                  {/* {jobTypes.map((type) => ( */}
                    {/* <div key={type} className="flex items-center space-x-2"> */}
                      {/* <Checkbox */}
                        {/* id={`job-type-${type}`} */}
                        {/* checked={filters.jobTypes.includes(type)} */}
                        {/* onCheckedChange={() => toggleArrayItem("jobTypes", type)} */}
                      {/* /> */}
                      {/* <Label htmlFor={`job-type-${type}`}>{type}</Label> */}
                    {/* </div> */}
                  {/* ))} */}
                {/* </div> */}
              {/* </div> */}

              {/* Location */}
              {/* <div className="space-y-2"> */}
                {/* <h3 className="font-medium">Location</h3> */}
                {/* <div className="grid grid-cols-2 gap-2"> */}
                  {/* {locations.map((location) => ( */}
                    {/* <div key={location} className="flex items-center space-x-2"> */}
                      {/* <Checkbox */}
                        {/* id={`location-${location}`} */}
                        {/* checked={filters.locations.includes(location)} */}
                        {/* onCheckedChange={() => toggleArrayItem("locations", location)} */}
                      {/* /> */}
                      {/* <Label htmlFor={`location-${location}`}>{location}</Label> */}
                    {/* </div> */}
                  {/* ))} */}
                {/* </div> */}
              {/* </div> */}

              {/* Experience Level */}
              {/* <div className="space-y-2"> */}
                {/* <h3 className="font-medium">Experience Level</h3> */}
                {/* <Select */}
                  {/* value={filters.experienceLevels[0] || ""} */}
                  {/* onValueChange={(value) => updateFilters("experienceLevels", value ? [value] : [])} */}
                {/* > */}
                  {/* <SelectTrigger> */}
                    {/* <SelectValue placeholder="Select experience level" /> */}
                  {/* </SelectTrigger> */}
                  {/* <SelectContent> */}
                    {/* {experienceLevels.map((level) => ( */}
                      {/* <SelectItem key={level} value={level}> */}
                        {/* {level} */}
                      {/* </SelectItem> */}
                    {/* ))} */}
                  {/* </SelectContent> */}
                {/* </Select> */}
              {/* </div> */}

              {/* Salary Range */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Salary Range (K)</h3>
                  <span className="text-sm">
                    ${filters.salaryRange[0]}K - ${filters.salaryRange[1]}K
                  </span>
                </div>
                <Slider
                  defaultValue={[50, 150]}
                  min={30}
                  max={250}
                  step={5}
                  value={filters.salaryRange}
                  onValueChange={(value) => updateFilters("salaryRange", value)}
                  className="py-4"
                />
              </div>

              {/* Skills */}
              <div className="space-y-2">
                <h3 className="font-medium">Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {skillsList.map((skill) => (
                    <Badge
                      key={skill}
                      variant={filters.skills.includes(skill) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleArrayItem("skills", skill)}
                    >
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Remote */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="remote-only"
                  checked={filters.remote}
                  onCheckedChange={(checked) => updateFilters("remote", !!checked)}
                />
                <Label htmlFor="remote-only">Remote Only</Label>
              </div>
            </div>

            <SheetFooter className="flex flex-row gap-2 sm:space-x-0">
              <Button variant="outline" onClick={resetFilters} className="flex-1">
                Reset
              </Button>
              <Button onClick={applyFilters} className="flex-1">
                Apply Filters
              </Button>
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </div>

      {/* Active filters display */}
      {activeFiltersCount > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {/* {filters.jobTypes.map((type) => (
            <Badge key={type} variant="secondary" className="gap-1">
              {type}
              <button 
                className="hover:opacity-80 focus:outline-none"
                onClick={() => toggleArrayItem("jobTypes", type)}
              >
                ×
              </button>
            </Badge>
          ))} */}

          {/* {filters.locations.map((location) => (
            <Badge key={location} variant="secondary" className="gap-1">
              {location}
              <button 
                className="hover:opacity-80 focus:outline-none"
                onClick={() => toggleArrayItem("locations", location)}
              >
                ×
              </button>
            </Badge>
          ))} */}

          {/* {filters.experienceLevels.map((level) => (
            <Badge key={level} variant="secondary" className="gap-1">
              {level}
              <button 
                className="hover:opacity-80 focus:outline-none"
                onClick={() => toggleArrayItem("experienceLevels", level)}
              >
                ×
              </button>
            </Badge>
          ))} */}

          {filters.skills.map((skill) => (
            <Badge key={skill} variant="secondary" className="gap-1">
              {skill}
              <button 
                className="hover:opacity-80 focus:outline-none"
                onClick={() => toggleArrayItem("skills", skill)}
              >
                ×
              </button>
            </Badge>
          ))}

          {(filters.salaryRange[0] > 50 || filters.salaryRange[1] < 150) && (
            <Badge variant="secondary" className="gap-1">
              ${filters.salaryRange[0]}K - ${filters.salaryRange[1]}K
              <button 
                className="hover:opacity-80 focus:outline-none"
                onClick={() => updateFilters("salaryRange", [50, 150])}
              >
                ×
              </button>
            </Badge>
          )}

          {filters.remote && (
            <Badge variant="secondary" className="gap-1">
              Remote Only
              <button 
                className="hover:opacity-80 focus:outline-none"
                onClick={() => updateFilters("remote", false)}
              >
                ×
              </button>
            </Badge>
          )}

          <Button variant="ghost" size="sm" onClick={resetFilters} className="text-xs h-6 px-2">
            Clear All
          </Button>
        </div>
      )}
    </div>
  )
}
