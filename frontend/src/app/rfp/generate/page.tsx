"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { type Supplier } from "@/lib/api"

export default function GenerateRFPPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const searchParams = useSearchParams()

  const [supplier, setSupplier] = useState<Supplier | null>(null)
  const [title, setTitle] = useState("")
  const [industry, setIndustry] = useState("")
  const [location, setLocation] = useState("")
  const [deliveryDate, setDeliveryDate] = useState("")
  const [budget, setBudget] = useState("")
  const [projectDescription, setProjectDescription] = useState("")
  const [contractLength, setContractLength] = useState("")
  const [standards, setStandards] = useState("")
  const [additionalRequirements, setAdditionalRequirements] = useState("")
  const [evaluationCriteria, setEvaluationCriteria] = useState([
    { name: "Technical Capability", key: "technical_capability", weight: 30 },
    { name: "Pricing Competitiveness", key: "pricing_competitiveness", weight: 30 },
    { name: "Delivery Reliability", key: "delivery_reliability", weight: 20 },
    { name: "Quality Assurance", key: "quality_assurance", weight: 15 },
    { name: "Customer Service", key: "customer_service", weight: 5 }
  ])
  const [additionalCriteria, setAdditionalCriteria] = useState("")
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
        setIndustry(productParam || "")
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
            product: searchParams.get("product") || industry,
            location: searchParams.get("location") || location,
            priceMin: searchParams.get("priceMin") || "",
            priceMax: searchParams.get("priceMax") || "",
          },
          rfp_requirements: {
            title,
            industry,
            location,
            deliveryDate,
            budget,
            projectDescription,
            standards: standards,
            additionalRequirements,
            evaluationCriteria: evaluationCriteria.reduce((acc, criterion) => {
              acc[criterion.key] = criterion.weight / 100;
              return acc;
            }, {} as Record<string, number>),
            additionalCriteria,
            client_name: session.user?.name || "Nexa",
            submission_deadline: "TBD",
            submission_email: session.user?.email || "procurement@nexa.org",
            contract_length: contractLength,
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
                  router.push("/supplier-search?loadSession=true")
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
            <p className="text-slate-600 mb-2">
              Fill in the details below to generate a comprehensive Request for Proposal
            </p>
            <p className="text-sm text-slate-500 mb-6">
              Fields marked with * are mandatory
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
                    Industry
                  </label>
                  <input
                    type="text"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
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
                  Project Description
                </label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Describe the project, its goals, and context..."
                  rows={4}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors resize-none"
                />
                <p className="text-xs text-slate-500 mt-1">Provide context about your project to help generate a more tailored RFP</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Contract Length
                </label>
                <input
                  type="text"
                  value={contractLength}
                  onChange={(e) => setContractLength(e.target.value)}
                  placeholder="e.g., 1 year, 2 years with renewal"
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                />
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

              {/* Evaluation Criteria */}
              <div className="border-2 border-slate-200 rounded-lg p-6 bg-white">
                <label className="block text-sm font-medium text-slate-700 mb-4">
                  Evaluation Criteria (Must total 100%)
                </label>
                <div className="space-y-3">
                  {evaluationCriteria.map((criterion, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <input
                        type="text"
                        value={criterion.name}
                        onChange={(e) => {
                          const updated = [...evaluationCriteria];
                          updated[index].name = e.target.value;
                          setEvaluationCriteria(updated);
                        }}
                        placeholder="Criterion name"
                        className="flex-1 px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none text-sm"
                      />
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={criterion.weight}
                        onChange={(e) => {
                          const updated = [...evaluationCriteria];
                          updated[index].weight = Number(e.target.value);
                          setEvaluationCriteria(updated);
                        }}
                        className="w-20 px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none text-sm"
                      />
                      <span className="text-sm text-slate-600">%</span>
                    </div>
                  ))}
                  <div className="pt-2 border-t border-slate-300">
                    <div className="flex items-center gap-3">
                      <span className="flex-1 text-sm font-medium text-slate-700">Total</span>
                      <span className={`w-20 text-sm font-bold ${
                        evaluationCriteria.reduce((sum, c) => sum + c.weight, 0) === 100
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}>
                        {evaluationCriteria.reduce((sum, c) => sum + c.weight, 0)}%
                      </span>
                      <span className="text-sm text-transparent">%</span>
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Additional Evaluation Notes
                  </label>
                  <textarea
                    value={additionalCriteria}
                    onChange={(e) => setAdditionalCriteria(e.target.value)}
                    placeholder="Add any additional evaluation criteria, scoring details, or notes that should be considered..."
                    rows={4}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors resize-none"
                  />
                  <p className="text-xs text-slate-500 mt-1">This will be included in the Evaluation Criteria section</p>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                variant="hero"
                size="lg"
                className="w-full hover:shadow-md hover:scale-[1.02] transition-transform"
              >
                {loading ? "Generating RFP..." : "Generate RFP"}
              </Button>

              {loading && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="inline-block h-5 w-5 animate-spin rounded-full border-3 border-solid border-blue-600 border-r-transparent"></div>
                    <div className="text-sm text-blue-800">
                      <p className="font-semibold">Generating your RFP...</p>
                      <p className="text-xs mt-1">Nexa is creating each section. This may take 30-60 seconds.</p>
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
                  <Button
                    onClick={handleViewRFP}
                    variant="hero"
                    className="hover:shadow-md hover:scale-[1.02] transition-transform"
                  >
                    View Document
                  </Button>
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
