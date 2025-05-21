"use client";

import {
  Briefcase,
  Home,
  BookmarkCheck,
  Settings,
} from "lucide-react";
import { SidebarHeader, SidebarFooter } from "@/components/ui/sidebar";
import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { useUser } from "@clerk/nextjs";

export default function JobSidebar() {
  const { user } = useUser();
  const email = user?.emailAddresses[0]?.emailAddress || "user@test.com";
  const name = email.split("@")[0]; // Get name before '@'

  return (
    <div className="flex flex-col h-full z-20">
      <SidebarHeader>
        <div className="flex items-center gap-2">
          <Briefcase className="h-5 w-5" />
          <span className="font-semibold">IntelliJobs</span>
        </div>
      </SidebarHeader>
      <div className="flex-1 overflow-auto p-4">
        <nav className="space-y-1">
          <Link
            href="/"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50"
          >
            <Home className="h-4 w-4" />
            Dashboard
          </Link>
          <Link
            href="/saved"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50"
          >
            <BookmarkCheck className="h-4 w-4" />
            Saved Jobs
          </Link>
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50"
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
        </nav>
      </div>
      <SidebarFooter>
        <div className="flex items-center gap-2">
          <UserButton
            afterSignOutUrl="/"
            appearance={{
              elements: {
                avatarBox: "h-8 w-8"
              }
            }}
          />
          <div className="flex flex-col">
            <span className="text-sm font-medium">{name}</span>
            <span className="text-xs text-gray-500">{email}</span>
          </div>
        </div>
      </SidebarFooter>
    </div>
  );
}