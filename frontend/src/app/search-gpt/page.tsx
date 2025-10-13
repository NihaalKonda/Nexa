"use client"

import { useState } from "react"
import Link from "next/link"
import { searchSuppliers, searchSuppliersDetailed, type Supplier } from "@/lib/api"

export default function SearchGPTPage() {
  const [product, setProduct] = useState("")
  const [location, setLocation] = useState("")
  const [priceMin, setPriceMin] = useState("")
  const [priceMax, setPriceMax] = useState("")
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [useDetailed, setUseDetailed] = useState(false)

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
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Nexa
          </Link>
          <nav className="flex gap-6">
            <Link href="/search" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Search
            </Link>
            <Link href="/search-gpt" className="text-sm font-medium text-blue-600">
              GPT Search
            </Link>
            <Link href="/dashboard" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Search Form */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
              GPT-Powered Supplier Search
            </h1>
            <p className="text-slate-600 mb-6">
              Search for suppliers using AI-powered web search with government contracts and reviews
            </p>

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

              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Searching..." : "Search Suppliers"}
              </button>
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        {suppliers.length > 0 && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900">
                Found {suppliers.length} {suppliers.length === 1 ? "supplier" : "suppliers"}
              </h2>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {suppliers.map((supplier, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all border border-slate-200 overflow-hidden"
                >
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-slate-900">
                          {supplier.name}
                        </h3>
                        <p className="text-slate-600 mt-1">{supplier.location}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-blue-600">
                          {supplier.price_range}
                        </div>
                      </div>
                    </div>

                    {/* Product Info */}
                    <div className="mb-4 pb-4 border-b border-slate-100">
                      <div className="text-lg font-semibold text-slate-800 mb-1">
                        {supplier.product_title}
                      </div>
                      <div className="text-sm text-slate-600">
                        Units: {supplier.units_sold}
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-slate-700 mb-4">{supplier.description}</p>

                    {/* Contact */}
                    <div className="mb-4 space-y-2">
                      {supplier.website && supplier.website !== "N/A" && (
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium text-slate-700">Website:</span>
                          <a
                            href={supplier.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            {supplier.website}
                          </a>
                        </div>
                      )}
                      {supplier.contact && supplier.contact !== "N/A" && (
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium text-slate-700">Contact:</span>
                          <span className="text-slate-600">{supplier.contact}</span>
                        </div>
                      )}
                    </div>

                    {/* Contracts & Reviews (if detailed search) */}
                    {supplier.past_contracts && (
                      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                        <div className="font-medium text-slate-900 mb-2">
                          Government Contracts
                        </div>
                        <div className="text-sm text-slate-700">
                          {supplier.past_contracts}
                        </div>
                      </div>
                    )}

                    {supplier.reviews_mentions && (
                      <div className="p-4 bg-green-50 rounded-lg">
                        <div className="font-medium text-slate-900 mb-2">
                          Reviews & Mentions
                        </div>
                        <div className="text-sm text-slate-700">
                          {supplier.reviews_mentions}
                        </div>
                      </div>
                    )}
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
