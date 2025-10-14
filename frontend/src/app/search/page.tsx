"use client"

import { useState } from "react"
import Link from "next/link"

// Hardcoded sample data
const SAMPLE_PRODUCTS = [
  {
    id: "1",
    name: "Industrial Valve Type A",
    sku: "IV-A-001",
    mpn: "MPN12345",
    price: "$150.00",
    currency: "USD",
    unit: "each",
    inStock: true,
    supplier: {
      name: "Industrial Parts Co.",
      verified: true,
      rating: 4.5,
      country: "USA",
    },
    certifications: ["ISO 9001", "CE", "UL"],
    description: "High-pressure industrial valve for heavy-duty applications",
  },
  {
    id: "2",
    name: "Steel Pipe 6 inch",
    sku: "SP-6-001",
    mpn: "SP6-2024",
    price: "$45.00",
    currency: "USD",
    unit: "ft",
    inStock: true,
    supplier: {
      name: "Industrial Parts Co.",
      verified: true,
      rating: 4.5,
      country: "USA",
    },
    certifications: ["ASTM A53"],
    description: "Schedule 40 carbon steel pipe, 6 inch diameter",
  },
  {
    id: "3",
    name: "Hydraulic Cylinder HC200",
    sku: "HC-200",
    mpn: "HC200-XL",
    price: "$850.00",
    currency: "USD",
    unit: "each",
    inStock: true,
    supplier: {
      name: "Global Manufacturing Ltd",
      verified: true,
      rating: 4.2,
      country: "China",
    },
    certifications: ["ISO 9001", "CE"],
    description: "Heavy-duty hydraulic cylinder, 200mm bore, 500mm stroke",
  },
  {
    id: "4",
    name: "Stainless Steel Fastener Kit",
    sku: "SSF-KIT-100",
    mpn: "SSF100",
    price: "$89.99",
    currency: "USD",
    unit: "kit",
    inStock: false,
    supplier: {
      name: "Precision Hardware Inc.",
      verified: false,
      rating: 3.8,
      country: "USA",
    },
    certifications: ["ASTM F593"],
    description: "100-piece 316 stainless steel fastener assortment",
  },
  {
    id: "5",
    name: "Electric Motor 3HP",
    sku: "EM-3HP-001",
    mpn: "EM3HP230V",
    price: "$425.00",
    currency: "USD",
    unit: "each",
    inStock: true,
    supplier: {
      name: "Motor World Supply",
      verified: true,
      rating: 4.7,
      country: "USA",
    },
    certifications: ["UL", "CSA", "NEMA"],
    description: "3HP electric motor, 230V, 3-phase, 1750 RPM",
  },
]

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [filteredProducts, setFilteredProducts] = useState(SAMPLE_PRODUCTS)

  const handleSearch = (query: string) => {
    setSearchQuery(query)

    if (!query.trim()) {
      setFilteredProducts(SAMPLE_PRODUCTS)
      return
    }

    const filtered = SAMPLE_PRODUCTS.filter((product) => {
      const searchLower = query.toLowerCase()
      return (
        product.name.toLowerCase().includes(searchLower) ||
        product.sku.toLowerCase().includes(searchLower) ||
        product.mpn.toLowerCase().includes(searchLower) ||
        product.supplier.name.toLowerCase().includes(searchLower) ||
        product.description.toLowerCase().includes(searchLower)
      )
    })

    setFilteredProducts(filtered)
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
            <Link href="/dashboard" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Search Bar */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
              Find Industrial Products
            </h1>
            <p className="text-slate-600 mb-6">
              Search across thousands of suppliers and products
            </p>

            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search by product name, SKU, MPN, or supplier..."
                className="w-full px-6 py-4 text-lg border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
              />
              <svg
                className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>

            <div className="mt-4 text-sm text-slate-500">
              {filteredProducts.length} {filteredProducts.length === 1 ? "result" : "results"} found
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all border border-slate-200 overflow-hidden group"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                        {product.name}
                      </h3>
                      <div className="flex gap-3 mt-2 text-sm font-mono text-slate-500">
                        <span>SKU: {product.sku}</span>
                        <span>•</span>
                        <span>MPN: {product.mpn}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {product.price}
                      </div>
                      <div className="text-sm text-slate-500">per {product.unit}</div>
                    </div>
                  </div>

                  {/* Supplier */}
                  <div className="flex items-center gap-2 mb-4 pb-4 border-b border-slate-100">
                    <div className="flex items-center gap-2 flex-1">
                      <span className="text-sm font-medium text-slate-700">
                        {product.supplier.name}
                      </span>
                      {product.supplier.verified && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fillRule="evenodd"
                              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                              clipRule="evenodd"
                            />
                          </svg>
                          Verified
                        </span>
                      )}
                      <span className="text-xs text-slate-500">
                        ⭐ {product.supplier.rating}
                      </span>
                    </div>
                    <span className="text-xs text-slate-500">{product.supplier.country}</span>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-slate-600 mb-4">{product.description}</p>

                  {/* Certifications */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {product.certifications.map((cert) => (
                      <span
                        key={cert}
                        className="px-2 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700"
                      >
                        {cert}
                      </span>
                    ))}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                    <div className="flex items-center gap-2">
                      {product.inStock ? (
                        <span className="inline-flex items-center gap-1 text-sm font-medium text-green-600">
                          <span className="w-2 h-2 rounded-full bg-green-600"></span>
                          In Stock
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-sm font-medium text-red-600">
                          <span className="w-2 h-2 rounded-full bg-red-600"></span>
                          Out of Stock
                        </span>
                      )}
                    </div>
                    <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredProducts.length === 0 && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">No products found</h3>
              <p className="text-slate-600">
                Try searching for something else, like "valve", "pipe", or "motor"
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
