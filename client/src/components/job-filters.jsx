"use client"
import { useState } from "react"
import { Filter } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, SheetFooter } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"

export default function JobFilters({ onFiltersChange }) {
  const [filters, setFilters] = useState({
    salaryRange: [50, 150],
    skills: [],
    remote: false,
  })
  const [isOpen, setIsOpen] = useState(false)
  const skillsList = [
    "JavaScript", "React", "TypeScript", "Node.js",
    "Python", "AWS", "Docker", "UI/UX", "Figma"
  ]

  // Count each selected skill, plus remote and salary range as additional filters
  const getActiveFiltersCount = (filtersObj) => {
    let count = 0
    count += filtersObj.skills.length
    if (filtersObj.remote) count += 1
    if (filtersObj.salaryRange[0] > 50 || filtersObj.salaryRange[1] < 150) count += 1
    return count
  }

  const updateFilters = (key, value) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
  }

  const toggleArrayItem = (key, item) => {
    setFilters((prev) => {
      const array = prev[key]
      const newArray = array.includes(item)
        ? array.filter((i) => i !== item)
        : [...array, item]
      return { ...prev, [key]: newArray }
    })
  }

  const resetFilters = () => {
    const reset = {
      salaryRange: [50, 150],
      skills: [],
      remote: false,
    }
    setFilters(reset)
    onFiltersChange(reset)
  }

  const applyFilters = () => {
    onFiltersChange(filters)
    setIsOpen(false)
  }

  const activeFiltersCount = getActiveFiltersCount(filters)

  return (
    <div className="mb-4 flex items-center">
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button
            variant="outline"
            className="flex items-center gap-2 px-4 py-2 text-base font-semibold"
          >
            <Filter className="w-5 h-5" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge className="ml-2 px-2 py-0.5 text-xs bg-primary text-primary-foreground">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
        </SheetTrigger>
        <SheetContent side="right" className="max-w-xs w-full px-5">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              <Filter className="w-5 h-5" />
              Filters
            </SheetTitle>
          </SheetHeader>
          <div className="py-4 space-y-6">
            <div>
              <Label className="block mb-2 font-medium">Skills</Label>
              <div className="flex flex-wrap gap-2">
                {skillsList.map((skill) => (
                  <Badge
                    key={skill}
                    onClick={() => toggleArrayItem("skills", skill)}
                    className={`cursor-pointer px-3 py-1 text-sm ${
                      filters.skills.includes(skill)
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <Label className="block mb-2 font-medium">Salary Range ($k)</Label>
              <Slider
                min={50}
                max={150}
                step={5}
                value={filters.salaryRange}
                onValueChange={(v) => updateFilters("salaryRange", v)}
                className="w-full"
              />
              <div className="flex justify-between text-xs mt-1">
                <span>{filters.salaryRange[0]}</span>
                <span>{filters.salaryRange[1]}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="remote"
                checked={filters.remote}
                onCheckedChange={(v) => updateFilters("remote", v)}
              />
              <Label htmlFor="remote" className="font-medium">Remote Only</Label>
            </div>
          </div>
          <SheetFooter className="flex flex-col gap-2 mt-6">
            <Button variant="default" className="w-full" onClick={applyFilters}>
              Apply Filters
            </Button>
            <Button variant="ghost" className="w-full" onClick={resetFilters}>
              Reset Filters
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </div>
  )
}
