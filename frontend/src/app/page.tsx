"use client"

import { useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import LandingNav from "@/components/landing/LandingNav"
import Hero from "@/components/landing/Hero"
import Features from "@/components/landing/Features"
import Benefits from "@/components/landing/Benefits"
import CTA from "@/components/landing/CTA"
import Footer from "@/components/landing/Footer"

export default function Home() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "authenticated" && session?.user) {
      const user = session.user as any
      // Only redirect once we have role information
      if (user.role) {
        if (user.role === "supplier") {
          router.push("/supplier/profile")
        } else if (user.role === "buyer") {
          router.push("/supplier-search")
        }
      }
    }
  }, [status, session, router])

  // Show loading while checking auth or redirecting
  if (status === "loading" || status === "authenticated") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Show landing page if not authenticated
  return (
    <div className="min-h-screen">
      <LandingNav />
      <main>
        <Hero />
        <Features />
        <Benefits />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}