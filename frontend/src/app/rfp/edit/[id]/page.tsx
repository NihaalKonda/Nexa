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

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    }
  }, [status, router])

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
                onClick={() => router.push("/supplier-search")}
                variant="ghost"
              >
                Supplier Search
              </Button>
              <Button
                onClick={() => router.push("/rfp-dashboard")}
                variant="ghost"
              >
                RFP Dashboard
              </Button>
              <Button
                onClick={() => signOut({ callbackUrl: "/" })}
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
