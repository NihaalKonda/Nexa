"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"

interface Product {
  id: string
  name: string
  sku: string | null
  mpn: string | null
  priceText: string | null
  currency: string | null
  unit: string | null
  description: string | null
  imageUrl: string | null
  inStock: boolean
  createdAt: string
  updatedAt: string
}

interface EditableProduct extends Product {
  isSaving?: boolean
  isNew?: boolean
}

export default function SupplierProducts() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [products, setProducts] = useState<EditableProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Redirect if not authenticated or not a supplier
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    } else if (status === "authenticated" && (session?.user as any)?.role !== "supplier") {
      router.push("/supplier-search")
    }
  }, [status, session, router])

  // Load products
  useEffect(() => {
    const fetchProducts = async () => {
      if (status === "authenticated") {
        try {
          setLoading(true)
          const response = await fetch("/api/supplier/products")
          const data = await response.json()

          if (response.ok) {
            setProducts(data.products)
          } else {
            setError(data.error || "Failed to load products")
          }
        } catch (err) {
          console.error("Error loading products:", err)
          setError("Failed to load products")
        } finally {
          setLoading(false)
        }
      }
    }

    fetchProducts()
  }, [status])

  const handleProductChange = (productId: string, field: keyof Product, value: any) => {
    setProducts(products.map(p =>
      p.id === productId ? { ...p, [field]: value } : p
    ))
  }

  const handleAddProduct = () => {
    const newProduct: EditableProduct = {
      id: `temp-${Date.now()}`,
      name: "",
      sku: null,
      mpn: null,
      priceText: null,
      currency: "USD",
      unit: null,
      description: null,
      imageUrl: null,
      inStock: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isNew: true,
    }
    setProducts([...products, newProduct])
  }

  const handleSave = async (productId: string) => {
    const product = products.find(p => p.id === productId)
    if (!product) return

    // Validate required fields
    if (!product.name || !product.unit || !product.priceText) {
      setError("Please fill in all required fields (Name, Unit, Price)")
      setSuccessMessage("")
      return
    }

    // Set saving state
    setProducts(products.map(p =>
      p.id === productId ? { ...p, isSaving: true } : p
    ))

    try {
      const isNew = product.isNew
      const url = isNew ? "/api/supplier/products" : `/api/supplier/products/${productId}`
      const method = isNew ? "POST" : "PUT"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: product.name,
          sku: product.sku,
          mpn: product.mpn,
          priceText: product.priceText,
          currency: product.currency,
          unit: product.unit,
          description: product.description,
          imageUrl: product.imageUrl,
          inStock: product.inStock,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        // If it's a new product, replace the temp ID with the real one
        if (isNew) {
          setProducts(products.map(p =>
            p.id === productId ? { ...data.product, isSaving: false, isNew: false } : p
          ))
          setSuccessMessage("Product added successfully!")
        } else {
          setProducts(products.map(p =>
            p.id === productId ? { ...p, isSaving: false } : p
          ))
          setSuccessMessage("Product saved successfully!")
        }
        setError("")
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(""), 3000)
      } else {
        setError(data.error || "Failed to save product")
        setSuccessMessage("")
        setProducts(products.map(p =>
          p.id === productId ? { ...p, isSaving: false } : p
        ))
      }
    } catch (err) {
      console.error("Error saving product:", err)
      setError("Failed to save product")
      setSuccessMessage("")
      setProducts(products.map(p =>
        p.id === productId ? { ...p, isSaving: false } : p
      ))
    }
  }

  const handleDelete = async (productId: string) => {
    const product = products.find(p => p.id === productId)

    // If it's a new product that hasn't been saved yet, just remove it from the list
    if (product?.isNew) {
      setProducts(products.filter(p => p.id !== productId))
      setSuccessMessage("Product removed successfully!")
      setError("")
      setTimeout(() => setSuccessMessage(""), 3000)
      return
    }

    try {
      const response = await fetch(`/api/supplier/products/${productId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        setProducts(products.filter(p => p.id !== productId))
        setSuccessMessage("Product removed successfully!")
        setError("")
        setTimeout(() => setSuccessMessage(""), 3000)
      } else {
        const data = await response.json()
        setError(data.error || "Failed to delete product")
        setSuccessMessage("")
      }
    } catch (err) {
      console.error("Error deleting product:", err)
      setError("Failed to delete product")
      setSuccessMessage("")
    }
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
      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-4 md:p-8 border border-slate-200">
            <div className="mb-8">
              <h1 className="text-2xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
                Product Catalog
              </h1>
              <p className="text-slate-600 mt-2">
                Manage your product listings
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {successMessage && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 text-sm">{successMessage}</p>
              </div>
            )}

            {loading ? (
              <div className="text-center py-16">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                <p className="mt-4 text-slate-600">Loading products...</p>
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">📦</div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">No products yet</h3>
                <p className="text-slate-600 mb-6">
                  Add your first product to start building your catalog
                </p>
                <Button
                  onClick={handleAddProduct}
                  variant="hero"
                  size="lg"
                >
                  + Add Your First Product
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">Your Products</h3>
                  <p className="text-sm text-slate-600">Edit your product catalog inline</p>
                </div>

                {products.map((product, index) => (
                  <div key={product.id} className="border-2 border-slate-200 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium text-slate-900">Product {index + 1}</h4>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => handleSave(product.id)}
                          disabled={product.isSaving}
                          className="text-blue-600 text-sm hover:text-blue-700 font-medium disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
                        >
                          {product.isSaving ? "Saving..." : "Save"}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(product.id)}
                          className="text-red-600 text-sm hover:text-red-700 font-medium cursor-pointer"
                        >
                          Remove
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Product Name *
                      </label>
                      <input
                        type="text"
                        value={product.name}
                        onChange={(e) => handleProductChange(product.id, 'name', e.target.value)}
                        className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                        placeholder="e.g., Aluminum Sheets 6061-T6"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          SKU
                        </label>
                        <input
                          type="text"
                          value={product.sku || ''}
                          onChange={(e) => handleProductChange(product.id, 'sku', e.target.value)}
                          className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                          placeholder="e.g., AL-6061-001"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          MPN
                        </label>
                        <input
                          type="text"
                          value={product.mpn || ''}
                          onChange={(e) => handleProductChange(product.id, 'mpn', e.target.value)}
                          className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                          placeholder="Manufacturer Part #"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Unit *
                      </label>
                      <input
                        type="text"
                        value={product.unit || ''}
                        onChange={(e) => handleProductChange(product.id, 'unit', e.target.value)}
                        className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                        placeholder="e.g., per sheet, per lb"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Price *
                        </label>
                        <input
                          type="text"
                          value={product.priceText || ''}
                          onChange={(e) => handleProductChange(product.id, 'priceText', e.target.value)}
                          className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                          placeholder="e.g., $85.00 or $2.50-$3.00"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Currency
                        </label>
                        <select
                          value={product.currency || 'USD'}
                          onChange={(e) => handleProductChange(product.id, 'currency', e.target.value)}
                          className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                        >
                          <option value="USD">USD</option>
                          <option value="EUR">EUR</option>
                          <option value="GBP">GBP</option>
                          <option value="CAD">CAD</option>
                          <option value="AUD">AUD</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Description
                      </label>
                      <textarea
                        value={product.description || ''}
                        onChange={(e) => handleProductChange(product.id, 'description', e.target.value)}
                        className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                        placeholder="Brief description of the product..."
                        rows={3}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Image URL
                      </label>
                      <input
                        type="url"
                        value={product.imageUrl || ''}
                        onChange={(e) => handleProductChange(product.id, 'imageUrl', e.target.value)}
                        className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg bg-white text-slate-700 focus:border-blue-500 focus:outline-none transition-colors"
                        placeholder="https://example.com/image.jpg"
                      />
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={product.inStock}
                        onChange={(e) => handleProductChange(product.id, 'inStock', e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-slate-700">
                        In Stock
                      </label>
                    </div>
                  </div>
                ))}

                <Button
                  type="button"
                  onClick={handleAddProduct}
                  variant="outline"
                  className="w-full"
                >
                  + Add Another Product
                </Button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
