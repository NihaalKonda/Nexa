"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

interface RFP {
  id: string
  title: string
  supplierName: string | null
  status: string
  createdAt: string
  updatedAt: string
  company: {
    name: string
    email: string
    city: string | null
    state: string | null
    country: string | null
  }
}

export default function SupplierRFPs() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [rfps, setRfps] = useState<RFP[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Redirect if not authenticated or not a supplier
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    } else if (status === "authenticated" && (session?.user as any)?.role !== "supplier") {
      router.push("/supplier-search")
    }
  }, [status, session, router])

  // Fetch RFPs
  useEffect(() => {
    if (status === "authenticated" && (session?.user as any)?.role === "supplier") {
      fetchRFPs()
    }
  }, [status, session])

  const fetchRFPs = async () => {
    try {
      setLoading(true)
      const response = await fetch("/api/supplier/rfps")

      if (!response.ok) {
        throw new Error("Failed to fetch RFPs")
      }

      const data = await response.json()
      setRfps(data.rfps || [])
    } catch (err) {
      console.error("Error fetching RFPs:", err)
      setError("Failed to load RFPs")
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      draft: "bg-gray-100 text-gray-800 border-gray-300",
      published: "bg-green-100 text-green-800 border-green-300",
      archived: "bg-slate-100 text-slate-600 border-slate-300",
    }

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold border ${statusStyles[status as keyof typeof statusStyles] || statusStyles.draft}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="container mx-auto px-3 md:px-6 py-3 md:py-4">
          <div className="flex items-center justify-between">
            <Link href="/supplier/profile" className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
              <Image
                src="/nexa_logo.png"
                alt="Nexa Logo"
                width={32}
                height={32}
                className="h-8 w-8"
              />
              <span className="text-xl lg:text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                Nexa
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-6">
              <Link href="/supplier/profile" className="text-base font-medium text-slate-700 hover:text-blue-600 transition-colors cursor-pointer">
                {session?.user?.name}
              </Link>
              <Button
                onClick={() => router.push("/supplier/products")}
                variant="ghost"
                className="text-sm px-4 py-2"
              >
                Products
              </Button>
              <Button
                onClick={() => router.push("/supplier/rfps")}
                variant="ghost"
                className="text-sm px-4 py-2"
              >
                RFPs
              </Button>
              <Button
                onClick={() => signOut({ callbackUrl: "/" })}
                variant="ghost"
                className="text-red-600 hover:text-red-700 text-sm px-4 py-2"
              >
                Sign Out
              </Button>
            </div>

            {/* Mobile Hamburger Menu */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {mobileMenuOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile Dropdown Menu */}
          {mobileMenuOpen && (
            <div className="lg:hidden mt-4 py-4 border-t border-gray-200">
              <div className="flex flex-col space-y-3">
                <div className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-50 rounded-lg">
                  {session?.user?.name}
                </div>
                <Button
                  onClick={() => {
                    router.push("/supplier/products")
                    setMobileMenuOpen(false)
                  }}
                  variant="ghost"
                  className="justify-start text-sm px-4 py-2"
                >
                  Products
                </Button>
                <Button
                  onClick={() => {
                    router.push("/supplier/rfps")
                    setMobileMenuOpen(false)
                  }}
                  variant="ghost"
                  className="justify-start text-sm px-4 py-2"
                >
                  RFPs
                </Button>
                <Button
                  onClick={() => signOut({ callbackUrl: "/" })}
                  variant="ghost"
                  className="justify-start text-red-600 hover:text-red-700 text-sm px-4 py-2"
                >
                  Sign Out
                </Button>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="pt-20 md:pt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              RFP Opportunities
            </h1>
            <p className="text-slate-600">
              View all RFPs that have been generated for your company
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
              <p className="mt-4 text-slate-600">Loading RFPs...</p>
            </div>
          ) : rfps.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">No RFPs yet</h3>
              <p className="text-slate-600">
                RFPs generated for your company will appear here
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {rfps.map((rfp) => (
                <div
                  key={rfp.id}
                  className="border-2 border-slate-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => window.open(`/api/rfp/${rfp.id}`, '_blank')}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-slate-900 mb-2">
                        {rfp.title}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-slate-600">
                        <div className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                          <span>{rfp.company.name}</span>
                        </div>
                        {rfp.company.city && rfp.company.state && (
                          <div className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <span>{rfp.company.city}, {rfp.company.state}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      {getStatusBadge(rfp.status)}
                      <span className="text-xs text-slate-500">
                        {formatDate(rfp.createdAt)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-sm text-slate-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span>{rfp.company.email}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          </div>
        </div>
      </div>
    </div>
  )
}
