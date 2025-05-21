import { Briefcase, Search, Bell, Bookmark, Sun, Moon, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useTheme } from "next-themes";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

export default function FloatingHeader() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="fixed top-0 left-0 right-0 z-10 bg-background/80 backdrop-blur-md border-b shadow-sm">
      <div className="container flex h-16 items-center px-4 sm:px-6">
        <SidebarTrigger className="mr-4 md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle sidebar</span>
        </SidebarTrigger>
        <div className="flex items-center gap-2 font-semibold md:hidden">
          <Briefcase className="h-5 w-5" />
          <span>JobFinder</span>
        </div>
        <div className="relative ml-auto flex items-center gap-4">
          <div className="relative w-full max-w-sm md:w-80">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              type="search" 
              placeholder="Search jobs..." 
              className="w-full bg-background/50 pl-8 md:w-80" 
            />
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
          >
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center">3</Badge>
                <span className="sr-only">Notifications</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <div className="flex items-center justify-between p-2 border-b">
                <span className="font-medium">Notifications</span>
                <Button variant="ghost" size="sm" className="text-xs">
                  Mark all as read
                </Button>
              </div>
              <DropdownMenuItem className="p-3 cursor-pointer">
                <div className="flex flex-col gap-1">
                  <div className="font-medium">Application Received</div>
                  <div className="text-sm text-muted-foreground">
                    TechCorp has received your application for Senior Frontend Developer
                  </div>
                  <div className="text-xs text-muted-foreground">2 hours ago</div>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem className="p-3 cursor-pointer">
                <div className="flex flex-col gap-1">
                  <div className="font-medium">Interview Invitation</div>
                  <div className="text-sm text-muted-foreground">
                    InnovateLabs would like to schedule an interview for Full Stack Engineer
                  </div>
                  <div className="text-xs text-muted-foreground">Yesterday</div>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem className="p-3 cursor-pointer">
                <div className="flex flex-col gap-1">
                  <div className="font-medium">New Job Match</div>
                  <div className="text-sm text-muted-foreground">We found 5 new jobs that match your profile</div>
                  <div className="text-xs text-muted-foreground">2 days ago</div>
                </div>
              </DropdownMenuItem>
              <div className="p-2 border-t">
                <Button variant="ghost" size="sm" className="w-full">
                  View all notifications
                </Button>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button variant="ghost" size="icon">
            <Bookmark className="h-5 w-5" />
            <span className="sr-only">Saved jobs</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
