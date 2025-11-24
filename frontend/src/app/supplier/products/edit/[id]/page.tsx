"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"

export default function EditProduct() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const params = useParams()
  const productId = params.id as string

  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const [formData, setFormData] = useState({
    name: "",
    sku: "",
    mpn: "",
    priceText: "",
    currency: "USD",
    unit: "",
    description: "",
    imageUrl: "",
    inStock: true,
  })

  // Load product data
  useEffect(() => {
    const fetchProduct = async () => {
      if (status === "authenticated") {
        try {
          setLoading(true)
          const response = await fetch(`/api/supplier/products/${productId}`)
          const data = await response.json()

          if (response.ok) {
            const product = data.product
            setFormData({
              name: product.name || "",
              sku: product.sku || "",
              mpn: product.mpn || "",
              priceText: product.priceText || "",
              currency: product.currency || "USD",
              unit: product.unit || "",
              description: product.description || "",
              imageUrl: product.imageUrl || "",
              inStock: product.inStock !== undefined ? product.inStock : true,
            })
          } else {
            setError(data.error || "Failed to load product")
          }
        } catch (err) {
          console.error("Error loading product:", err)
          setError("Failed to load product")
        } finally {
          setLoading(false)
        }
      }
    }

    if (productId) {
      fetchProduct()
    }
  }, [status, productId])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target

    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked
      setFormData(prev => ({ ...prev, [name]: checked }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError("")

    try {
      const response = await fetch(`/api/supplier/products/${productId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to update product")
      }

      router.push("/supplier/products")
    } catch (err: any) {
      console.error("Error updating product:", err)
      setError(err.message || "Failed to update product")
    } finally {
      setIsSaving(false)
    }
  }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
          <div className="text-center mb-8">
            <Link href="/supplier/products" className="inline-flex items-center gap-3 justify-center mb-4">
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
            <h2 className="text-2xl font-bold text-slate-900">Edit Product</h2>
            <p className="mt-2 text-sm text-slate-600">
              Update your product information
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Product Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="e.g., Aluminum Sheets 6061-T6"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  SKU
                </label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="e.g., AL-6061-001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  MPN
                </label>
                <input
                  type="text"
                  name="mpn"
                  value={formData.mpn}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="Manufacturer Part #"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Unit *
              </label>
              <input
                type="text"
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="e.g., per sheet, per lb"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Price *
              </label>
              <input
                type="text"
                name="priceText"
                value={formData.priceText}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="e.g., $85.00 or $2.50-$3.00"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Currency
              </label>
              <select
                name="currency"
                value={formData.currency}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="CAD">CAD</option>
                <option value="AUD">AUD</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Brief description of the product..."
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Image URL
              </label>
              <input
                type="url"
                name="imageUrl"
                value={formData.imageUrl}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="https://example.com/image.jpg"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="inStock"
                checked={formData.inStock}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
              />
              <label htmlFor="inStock" className="ml-2 block text-sm text-slate-700">
                In Stock
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                onClick={() => router.push("/supplier/products")}
                variant="outline"
                className="w-full"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSaving}
                variant="hero"
                className="w-full"
              >
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>

          <div className="mt-6 text-center">
            <Link href="/supplier/products" className="text-sm text-blue-600 font-medium hover:underline">
              Back to Products
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
