import { BarChart3, Briefcase, CheckCircle, Clock, Bookmark } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function StatsBox() {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Your Job Stats
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <StatItem icon={<Briefcase className="h-4 w-4 text-primary" />} label="Viewed" value={42} />
          <StatItem icon={<CheckCircle className="h-4 w-4 text-green-500" />} label="Applied" value={12} />
          <StatItem icon={<Clock className="h-4 w-4 text-orange-500" />} label="Pending" value={8} />
          <StatItem icon={<Bookmark className="h-4 w-4 text-purple-500" />} label="Saved" value={15} />
        </div>
      </CardContent>
    </Card>
  )
}

function StatItem({ icon, label, value }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border p-3">
      <div className="flex items-center gap-2">
        {icon}
        <span className="text-sm font-medium">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}
