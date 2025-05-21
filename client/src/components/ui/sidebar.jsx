"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const SidebarContext = React.createContext(null)

export function SidebarProvider({ children, className, ...props }) {
  const [isOpen, setIsOpen] = React.useState(true)

  return (
    <SidebarContext.Provider value={{ isOpen, setIsOpen }}>
      <div
        className={cn(
          "flex h-screen w-full bg-background",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </SidebarContext.Provider>
  )
}

export function SidebarInset({ children, className, ...props }) {
  const { isOpen } = React.useContext(SidebarContext)

  return (
    <div
      className={cn(
        "flex flex-col w-64 border-r bg-background",
        !isOpen && "hidden",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarContent({ children, className, ...props }) {
  return (
    <div
      className={cn(
        "flex-1 overflow-auto bg-background",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarHeader({ children, className, ...props }) {
  return (
    <div
      className={cn(
        "flex h-16 items-center border-b px-4 bg-background",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarFooter({ children, className, ...props }) {
  return (
    <div
      className={cn(
        "flex h-16 items-center border-t px-4 bg-background",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarToggle({ children, className, ...props }) {
  const { isOpen, setIsOpen } = React.useContext(SidebarContext)

  return (
    <button
      className={cn(
        "flex h-16 items-center border-b px-4 bg-background hover:bg-accent hover:text-accent-foreground",
        className
      )}
      onClick={() => setIsOpen(!isOpen)}
      {...props}
    >
      {children}
    </button>
  )
}

export function SidebarTrigger({ children, className, ...props }) {
  const { setIsOpen } = React.useContext(SidebarContext)

  return (
    <button
      className={cn(
        "flex items-center justify-center p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors",
        className
      )}
      onClick={() => setIsOpen((prev) => !prev)}
      {...props}
    >
      {children}
    </button>
  )
} 