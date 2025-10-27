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
  filename: string | null
  status: string
  createdAt: string
  updatedAt: string
}

export default function RFPDashboard() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [rfps, setRfps] = useState<RFP[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    }
  }, [status, router])

  // Fetch RFPs
  useEffect(() => {
    if (status === "authenticated") {
      fetchRFPs()
    }
  }, [status])

  const fetchRFPs = async () => {
    try {
      setLoading(true)
      const response = await fetch("/api/rfp/list")
      const data = await response.json()

      if (data.success) {
        setRfps(data.rfps)
      } else {
        setError("Failed to load RFPs")
      }
    } catch (err) {
      console.error("Error fetching RFPs:", err)
      setError("Failed to load RFPs")
    } finally {
      setLoading(false)
    }
  }

  const handleViewRFP = (rfpId: string) => {
    window.open(`/api/rfp/${rfpId}?format=pdf`, '_blank')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Show loading while checking auth
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

  // Don't render page if not authenticated
  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity">
              <Image
                src="/nexa_logo.png"
                alt="Nexa Logo"
                width={40}
                height={40}
                className="h-10 w-10"
              />
              <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                Nexa
              </span>
            </Link>

            <div className="flex items-center gap-6">
              <span className="text-base font-medium text-slate-700">{session.user?.name}</span>
              <Button
                onClick={() => {
                  router.push("/supplier-search")
                }}
                variant="ghost"
              >
                Supplier Search
              </Button>
              <Button
                onClick={() => {
                  signOut({ callbackUrl: "/" })
                }}
                variant="ghost"
                className="text-red-600 hover:text-red-700"
              >
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="max-w-6xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
              RFP Dashboard
            </h1>
            <p className="text-slate-600">View and manage all your generated RFPs</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-16">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
              <p className="mt-4 text-slate-600">Loading RFPs...</p>
            </div>
          )}

          {/* RFP List */}
          {!loading && rfps.length > 0 && (
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Title</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Filename</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Status</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Created</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rfps.map((rfp) => (
                      <tr key={rfp.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 text-sm text-slate-900 font-medium">{rfp.title}</td>
                        <td className="px-6 py-4 text-sm text-slate-600">{rfp.filename || 'N/A'}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            rfp.status === 'published' ? 'bg-green-100 text-green-800' :
                            rfp.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {rfp.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">{formatDate(rfp.createdAt)}</td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            <Button
                              onClick={() => router.push(`/rfp/edit/${rfp.id}`)}
                              variant="outline"
                              size="sm"
                            >
                              Edit
                            </Button>
                            <Button
                              onClick={() => handleViewRFP(rfp.id)}
                              variant="outline"
                              size="sm"
                            >
                              View PDF
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!loading && rfps.length === 0 && (
            <div className="text-center py-16 bg-white rounded-2xl shadow-xl border border-slate-200">
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">No RFPs yet</h3>
              <p className="text-slate-600 mb-6">
                Generate your first RFP to see it here
              </p>
              <Button
                onClick={() => router.push("/supplier-search")}
                variant="hero"
                size="lg"
              >
                Go to Supplier Search
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
