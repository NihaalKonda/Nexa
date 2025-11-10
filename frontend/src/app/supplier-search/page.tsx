"use client"

import { useState, useEffect, Suspense } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { searchSuppliers, searchSuppliersDetailed, type Supplier } from "@/lib/api"

function SearchGPTContent() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [product, setProduct] = useState("")
  const [location, setLocation] = useState("")
  const [priceMin, setPriceMin] = useState("")
  const [priceMax, setPriceMax] = useState("")
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [useDetailed, setUseDetailed] = useState(false)
  const [loadingSession, setLoadingSession] = useState(false)
  const [successMessage, setSuccessMessage] = useState("")
  const [sortBy, setSortBy] = useState<"score" | "price" | "contracts">("score")

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    }
  }, [status, router])

  // Auto-load session if loadSession query parameter is present
  useEffect(() => {
    const shouldLoadSession = searchParams.get("loadSession")
    if (shouldLoadSession === "true" && status === "authenticated") {
      handleLoadLastSession()
    }
  }, [searchParams, status])

  // Function to load last session
  const handleLoadLastSession = async () => {
    setLoadingSession(true)
    setError("")

    try {
      const response = await fetch("/api/search-queries")
      const data = await response.json()

      console.log("Load last session response:", data) // Debug log

      if (data.success && data.searchQuery && data.searchQuery.filters) {
        const filters = data.searchQuery.filters as any
        console.log("Filters:", filters) // Debug log

        // Restore search parameters
        setProduct(filters.product || "")
        setLocation(filters.location || "")
        setPriceMin(filters.priceMin?.toString() || "")
        setPriceMax(filters.priceMax?.toString() || "")

        // Restore search results if they exist
        if (filters.results && Array.isArray(filters.results)) {
          setSuppliers(filters.results)
          console.log("Loaded results:", filters.results.length) // Debug log
        } else {
          setSuppliers([])
        }

        // Show success message
        setSuccessMessage(`Session loaded successfully! ${filters.results?.length || 0} results restored.`)
        setTimeout(() => setSuccessMessage(""), 3000)
      } else {
        setError("No previous session found")
      }
    } catch (err) {
      console.error("Load session error:", err) // Debug log
      setError("Failed to load last session")
    } finally {
      setLoadingSession(false)
    }
  }

  // Function to save search query with results
  const saveSearchQuery = async (searchResults: Supplier[]) => {
    try {
      await fetch("/api/search-queries", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product,
          location,
          priceMin: parseFloat(priceMin) || 0,
          priceMax: parseFloat(priceMax) || 10000,
          resultsCount: searchResults.length,
          results: searchResults, // Save the actual results
        }),
      })
    } catch (err) {
      console.error("Failed to save search query:", err)
    }
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

  // Helper function to extract price as number for sorting
  const extractPriceValue = (priceRange: string): number => {
    const numbers = priceRange.match(/\d+\.?\d*/g)
    if (!numbers || numbers.length === 0) return 0
    // If there's a range, use the average
    const prices = numbers.map(n => parseFloat(n))
    return prices.reduce((a, b) => a + b, 0) / prices.length
  }

  // Helper function to count contracts
  const countContracts = (contracts?: string): number => {
    if (!contracts || contracts === "None found" || contracts === "None") return 0
    return contracts.split(';').filter(c => c.trim().length > 0).length
  }

  // Sort suppliers based on selected criteria
  const getSortedSuppliers = () => {
    const sorted = [...suppliers]

    switch (sortBy) {
      case "price":
        sorted.sort((a, b) => extractPriceValue(a.price_range) - extractPriceValue(b.price_range))
        break
      case "score":
        sorted.sort((a, b) => (b.score || 0) - (a.score || 0))
        break
      case "contracts":
        sorted.sort((a, b) => countContracts(b.past_contracts) - countContracts(a.past_contracts))
        break
    }

    return sorted
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const params = {
        product,
        location,
        price_min: parseFloat(priceMin) || 0,
        price_max: parseFloat(priceMax) || 10000,
      }

      const response = useDetailed
        ? await searchSuppliersDetailed(params)
        : await searchSuppliers(params)

      if (response.success) {
        setSuppliers(response.suppliers)
        // Save the search query and results to database
        await saveSearchQuery(response.suppliers)
      } else {
        setError(response.error || "Failed to search suppliers")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
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
                  router.push("/rfp-dashboard")
                }}
                variant="ghost"
              >
                RFP Dashboard
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
        {/* Search Form */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
                  AI-Powered Supplier Search
                </h1>
                <p className="text-slate-600">
                  Search for suppliers using AI-powered web search with government contracts and reviews
                </p>
              </div>
              <Button
                type="button"
                onClick={handleLoadLastSession}
                disabled={loadingSession}
                variant="outline"
                className="whitespace-nowrap"
              >
                {loadingSession ? "Loading..." : "Load Last Session"}
              </Button>
            </div>

            {successMessage && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                {successMessage}
              </div>
            )}

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Product
                </label>
                <input
                  type="text"
                  value={product}
                  onChange={(e) => setProduct(e.target.value)}
                  placeholder="e.g., aluminum sheets, industrial valves"
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g., Buffalo, New York"
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Min Price ($)
                  </label>
                  <input
                    type="number"
                    value={priceMin}
                    onChange={(e) => setPriceMin(e.target.value)}
                    placeholder="50"
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Max Price ($)
                  </label>
                  <input
                    type="number"
                    value={priceMax}
                    onChange={(e) => setPriceMax(e.target.value)}
                    placeholder="300"
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="detailed"
                  checked={useDetailed}
                  onChange={(e) => setUseDetailed(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="detailed" className="text-sm text-slate-700">
                  Include contracts & reviews (takes longer)
                </label>
              </div>

              <Button
                type="submit"
                disabled={loading}
                variant="hero"
                size="lg"
                className="w-full hover:shadow-md hover:scale-[1.02] transition-transform"
              >
                {loading ? "Searching..." : "Search Suppliers"}
              </Button>
            </form>
          </div>
        </div>

        {/* Results */}
        {suppliers.length > 0 && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-8 flex justify-between items-center">
              <h2 className="text-3xl font-bold text-slate-900">
                Found {suppliers.length} {suppliers.length === 1 ? "supplier" : "suppliers"}
              </h2>

              {/* Sort Dropdown */}
              <div className="flex items-center gap-3">
                <label htmlFor="sort" className="text-sm font-medium text-slate-700">
                  Sort by:
                </label>
                <select
                  id="sort"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as "score" | "price" | "contracts")}
                  className="px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors text-sm bg-white"
                >
                  <option value="score">Nexa Score</option>
                  <option value="price">Price (Low to High)</option>
                  <option value="contracts"># of Contracts</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
              {getSortedSuppliers().map((supplier, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-slate-200 overflow-hidden"
                >
                  <div className="p-5">
                    {/* Header */}
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-slate-900 mb-1">
                          {supplier.name}
                        </h3>
                        <p className="text-slate-600 text-sm">{supplier.location}</p>
                      </div>
                      <div className="text-right ml-4">
                        {supplier.score !== undefined && (
                          <div className="mb-2">
                            <span className="text-sm text-slate-600">Score: </span>
                            <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                              {supplier.score}/100
                            </span>
                          </div>
                        )}
                        <div>
                          <span className="text-sm text-slate-600">Price: </span>
                          <span className="text-base font-bold text-blue-600">
                            {supplier.price_range}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Product Info */}
                    <div className="mb-4 pb-4 border-b border-slate-200">
                      <div className="text-base font-semibold text-slate-800 mb-1">
                        {supplier.product_title}
                      </div>
                      <div className="text-sm text-slate-600">
                        Units: {supplier.units_sold}
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-slate-700 text-sm mb-4 leading-relaxed line-clamp-3">{supplier.description}</p>

                    {/* Contact */}
                    <div className="mb-4 space-y-2">
                      {supplier.website && supplier.website !== "N/A" && (
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-700 text-sm">Website:</span>
                          <a
                            href={supplier.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-700 hover:underline text-sm truncate"
                          >
                            {supplier.website}
                          </a>
                        </div>
                      )}
                      {supplier.contact && supplier.contact !== "N/A" && (
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-700 text-sm">Contact:</span>
                          <span className="text-slate-600 text-sm">{supplier.contact}</span>
                        </div>
                      )}
                    </div>

                    {/* Contracts & Reviews (if detailed search) */}
                    {supplier.past_contracts && (
                      <div className="mb-4 p-4 bg-blue-50 border border-blue-100 rounded-lg">
                        <div className="font-bold text-slate-900 mb-2 text-base">
                          Past Contracts
                        </div>
                        {supplier.past_contracts === "None found" || supplier.past_contracts === "None" ? (
                          <div className="text-xs text-slate-600 italic">No contracts found</div>
                        ) : (
                          <div className="space-y-2">
                            {supplier.past_contracts.split(';').map((contract, idx) => {
                              const match = contract.trim().match(/^(.+?):\s*\$?([\d,]+)\s*\((.+?)\s*-\s*(.+?)\)/)
                              if (match) {
                                const [, agency, amount, startDate, endDate] = match
                                return (
                                  <div key={idx} className="flex justify-between items-center text-xs bg-white p-2 rounded border border-blue-200">
                                    <div>
                                      <div className="font-semibold text-slate-800">{agency}</div>
                                      <div className="text-slate-600">{startDate} - {endDate}</div>
                                    </div>
                                    <div className="font-bold text-blue-600">${amount}</div>
                                  </div>
                                )
                              }
                              return null
                            })}
                          </div>
                        )}
                      </div>
                    )}

                    {supplier.reviews_mentions && (
                      <div className="p-4 bg-white border border-slate-200 rounded-lg">
                        <div className="font-bold text-slate-900 mb-2 text-base">
                          Reviews
                        </div>
                        <div className="text-sm text-slate-900 leading-relaxed max-h-24 overflow-y-auto">
                          {supplier.reviews_mentions}
                        </div>
                      </div>
                    )}

                    {/* Generate RFP Button */}
                    <div className="mt-6">
                      <Button
                        onClick={() => {
                          // Encode supplier data in URL params
                          const params = new URLSearchParams({
                            supplier: JSON.stringify(supplier),
                            product,
                            location,
                            priceMin,
                            priceMax,
                          })
                          router.push(`/rfp/generate?${params.toString()}`)
                        }}
                        variant="hero"
                        size="lg"
                        className="w-full hover:shadow-md hover:scale-[1.02] transition-transform"
                      >
                        Generate RFP for {supplier.name}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!loading && suppliers.length === 0 && !error && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-bold text-slate-900 mb-2">Ready to search</h3>
            <p className="text-slate-600">
              Enter your search criteria above to find suppliers using AI-powered search
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

export default function SearchGPTPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    }>
      <SearchGPTContent />
    </Suspense>
  )
}
