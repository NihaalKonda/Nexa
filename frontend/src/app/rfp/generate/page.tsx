"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { type Supplier } from "@/lib/api"

export default function GenerateRFPPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const searchParams = useSearchParams()

  const [supplier, setSupplier] = useState<Supplier | null>(null)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState("")
  const [location, setLocation] = useState("")
  const [deliveryDate, setDeliveryDate] = useState("")
  const [budget, setBudget] = useState("")
  const [standards, setStandards] = useState("")
  const [additionalRequirements, setAdditionalRequirements] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [generatedRFP, setGeneratedRFP] = useState<any>(null)

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    }
  }, [status, router])

  // Load supplier data from URL params
  useEffect(() => {
    const supplierParam = searchParams.get("supplier")
    const productParam = searchParams.get("product")
    const locationParam = searchParams.get("location")
    const priceMinParam = searchParams.get("priceMin")
    const priceMaxParam = searchParams.get("priceMax")

    if (supplierParam) {
      try {
        const parsedSupplier = JSON.parse(supplierParam)
        setSupplier(parsedSupplier)
        setTitle(`RFP for ${parsedSupplier.product_title || productParam}`)
        setCategory(productParam || "")
        setLocation(locationParam || parsedSupplier.location || "")

        if (priceMinParam && priceMaxParam) {
          setBudget(`$${priceMinParam} - $${priceMaxParam}`)
        }
      } catch (err) {
        console.error("Error parsing supplier data:", err)
        setError("Failed to load supplier information")
      }
    }
  }, [searchParams])

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

  const handleGenerateRFP = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      // Call Flask backend directly
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

      const response = await fetch(`${API_BASE_URL}/api/rfp/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          supplier: supplier,
          search_data: {
            product: searchParams.get("product") || category,
            location: searchParams.get("location") || location,
            priceMin: searchParams.get("priceMin") || "",
            priceMax: searchParams.get("priceMax") || "",
          },
          rfp_requirements: {
            title,
            category,
            location,
            deliveryDate,
            budget,
            standards: standards,
            additionalRequirements,
            client_name: "Nexa",
            submission_deadline: "TBD",
            submission_email: "procurement@nexa.org",
            contract_length: "1 year",
          },
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to generate RFP")
      }

      const data = await response.json()
      setGeneratedRFP(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  const handleViewRFP = () => {
    if (!generatedRFP?.pdf_filename) return

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"
    const viewUrl = `${API_BASE_URL}/api/rfp/download/${generatedRFP.pdf_filename}`

    // Open in new tab to view
    window.open(viewUrl, '_blank')
  }

  const handleDownloadRFP = () => {
    if (!generatedRFP?.pdf_filename) return

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"
    const downloadUrl = `${API_BASE_URL}/api/rfp/download/${generatedRFP.pdf_filename}`

    // Create a temporary link to trigger download
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = generatedRFP.pdf_filename
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Nexa
          </Link>
          <nav className="flex gap-6 items-center">
            <Link href="/search-gpt" className="text-sm font-medium hover:text-blue-600 transition-colors">
              AI Search
            </Link>
            <Link href="/dashboard" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
            <div className="h-4 w-px bg-slate-300"></div>
            <span className="text-sm text-slate-600">{session.user?.name}</span>
            <button
              onClick={() => {
                signOut({ callbackUrl: "/" })
              }}
              className="text-sm font-medium text-red-600 hover:text-red-700 transition-colors"
            >
              Sign Out
            </button>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Supplier Info Card */}
          {supplier && (
            <div className="bg-white rounded-xl shadow-md p-6 mb-8 border border-slate-200">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Selected Supplier</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-600">Supplier Name</p>
                  <p className="font-semibold text-slate-900">{supplier.name}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Location</p>
                  <p className="font-semibold text-slate-900">{supplier.location}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Product</p>
                  <p className="font-semibold text-slate-900">{supplier.product_title}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Price Range</p>
                  <p className="font-semibold text-slate-900">{supplier.price_range}</p>
                </div>
              </div>
            </div>
          )}

          {/* RFP Generation Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
              Generate RFP
            </h1>
            <p className="text-slate-600 mb-6">
              Fill in the details below to generate a comprehensive Request for Proposal
            </p>

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleGenerateRFP} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  RFP Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., RFP for Aluminum Sheet Supply"
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Category
                  </label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="e.g., Industrial Materials"
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Delivery Location
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g., Buffalo, New York"
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Expected Delivery Date
                  </label>
                  <input
                    type="date"
                    value={deliveryDate}
                    onChange={(e) => setDeliveryDate(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Budget Range
                  </label>
                  <input
                    type="text"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    placeholder="e.g., $50,000 - $100,000"
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Quality Standards & Certifications
                </label>
                <input
                  type="text"
                  value={standards}
                  onChange={(e) => setStandards(e.target.value)}
                  placeholder="e.g., ISO 9001, ASTM B209, AS9100 (comma-separated)"
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                />
                <p className="text-xs text-slate-500 mt-1">Separate multiple standards with commas</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Additional Requirements
                </label>
                <textarea
                  value={additionalRequirements}
                  onChange={(e) => setAdditionalRequirements(e.target.value)}
                  placeholder="Any specific requirements, terms, or conditions..."
                  rows={4}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading && (
                  <div className="inline-block h-5 w-5 animate-spin rounded-full border-3 border-solid border-white border-r-transparent"></div>
                )}
                {loading ? "Generating RFP with AI..." : "Generate RFP"}
              </button>

              {loading && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="inline-block h-5 w-5 animate-spin rounded-full border-3 border-solid border-blue-600 border-r-transparent"></div>
                    <div className="text-sm text-blue-800">
                      <p className="font-semibold">Generating your RFP...</p>
                      <p className="text-xs mt-1">GPT-4 is creating each section. This may take 30-60 seconds.</p>
                    </div>
                  </div>
                </div>
              )}
            </form>
          </div>

          {/* Generated RFP Preview */}
          {generatedRFP && (
            <div className="mt-8 bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-slate-900">Generated RFP</h2>
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(generatedRFP.markdown)
                      alert("RFP copied to clipboard!")
                    }}
                    className="px-4 py-2 text-sm font-medium text-slate-600 border-2 border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    Copy Markdown
                  </button>
                  <button
                    onClick={handleViewRFP}
                    className="px-4 py-2 text-sm font-medium text-blue-600 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    View Document
                  </button>
                  <button
                    onClick={handleDownloadRFP}
                    className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-md hover:shadow-lg"
                  >
                    Download HTML
                  </button>
                </div>
              </div>

              <div className="prose max-w-none">
                <div className="p-6 bg-slate-50 rounded-lg border border-slate-200 whitespace-pre-wrap font-mono text-sm">
                  {generatedRFP.markdown}
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                  <div className="text-sm text-green-800 flex-1">
                    <p className="font-semibold">RFP Generated Successfully!</p>
                    <p className="mt-1">Click "View RFP Document" above to open it. The document has a "Print/Save as PDF" button in the top right corner.</p>
                    <p className="mt-2 text-xs opacity-75">File: {generatedRFP.pdf_filename}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
