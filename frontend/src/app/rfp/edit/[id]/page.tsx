"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter, useParams } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

export default function EditRFPPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const params = useParams()
  const rfpId = params.id as string

  const [rfp, setRfp] = useState<any>(null)
  const [markdown, setMarkdown] = useState("")
  const [title, setTitle] = useState("")
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Redirect to signin if not authenticated or redirect suppliers to their profile
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    } else if (status === "authenticated") {
      const user = session?.user as any
      if (user?.role === "supplier") {
        router.push("/supplier/profile")
      }
    }
  }, [status, session, router])

  // Fetch RFP data
  useEffect(() => {
    if (status === "authenticated" && rfpId) {
      fetchRFP()
    }
  }, [status, rfpId])

  const fetchRFP = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/rfp/${rfpId}?format=json`)

      if (!response.ok) {
        throw new Error("Failed to fetch RFP")
      }

      const data = await response.json()
      setRfp(data)
      setMarkdown(data.bodyMd || "")
      setTitle(data.title || "")
    } catch (err) {
      console.error("Error fetching RFP:", err)
      setError("Failed to load RFP")
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError("")

      const response = await fetch(`/api/rfp/${rfpId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title,
          bodyMd: markdown,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to save RFP")
      }

      setSuccessMessage("RFP saved successfully!")
      setTimeout(() => setSuccessMessage(""), 3000)
    } catch (err) {
      console.error("Error saving RFP:", err)
      setError("Failed to save RFP")
    } finally {
      setSaving(false)
    }
  }

  const handlePreview = () => {
    window.open(`/api/rfp/${rfpId}?format=pdf`, '_blank')
  }

  // Show loading while checking auth
  if (status === "loading" || loading) {
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
        <div className="container mx-auto px-3 md:px-6 py-3 md:py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
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
              <Link href="/buyer/profile" className="text-base font-medium text-slate-700 hover:text-blue-600 transition-colors cursor-pointer">
                {session.user?.name}
              </Link>
              <div className="flex items-center gap-0">
                <Button
                  onClick={() => router.push("/supplier-search")}
                  variant="ghost"
                  className="text-sm px-4 py-2"
                >
                  Supplier Search
                </Button>
                <Button
                  onClick={() => router.push("/rfp-dashboard")}
                  variant="ghost"
                  className="text-sm px-4 py-2"
                >
                  RFP Dashboard
                </Button>
              </div>
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
                  {session.user?.name}
                </div>
                <Button
                  onClick={() => {
                    router.push("/supplier-search")
                    setMobileMenuOpen(false)
                  }}
                  variant="ghost"
                  className="justify-start text-sm px-4 py-2"
                >
                  Supplier Search
                </Button>
                <Button
                  onClick={() => {
                    router.push("/rfp-dashboard")
                    setMobileMenuOpen(false)
                  }}
                  variant="ghost"
                  className="justify-start text-sm px-4 py-2"
                >
                  RFP Dashboard
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

      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="max-w-6xl mx-auto">
          {/* Page Header */}
          <div className="mb-6">
            <div className="flex items-center gap-4 mb-4">
              <Button
                onClick={() => router.push("/rfp-dashboard")}
                variant="ghost"
                size="sm"
              >
                ← Back to Dashboard
              </Button>
            </div>
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
              Edit RFP
            </h1>
            <p className="text-slate-600">Make changes to your RFP document</p>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
              {successMessage}
            </div>
          )}

          {/* Edit Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <div className="space-y-6">
              {/* Title Input */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  RFP Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="Enter RFP title"
                />
              </div>

              {/* Markdown Editor */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  RFP Content (Markdown)
                </label>
                <textarea
                  value={markdown}
                  onChange={(e) => setMarkdown(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors font-mono text-sm"
                  rows={20}
                  placeholder="Enter RFP content in markdown format"
                />
                <p className="mt-2 text-xs text-slate-500">
                  Use markdown syntax for formatting (e.g., # for headers, ** for bold, - for lists)
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  variant="hero"
                  size="lg"
                  className="flex-1 hover:shadow-md hover:scale-[1.02] transition-transform"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
                <Button
                  onClick={handlePreview}
                  variant="outline"
                  size="lg"
                >
                  Preview PDF
                </Button>
                <Button
                  onClick={() => router.push("/rfp-dashboard")}
                  variant="ghost"
                  size="lg"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
