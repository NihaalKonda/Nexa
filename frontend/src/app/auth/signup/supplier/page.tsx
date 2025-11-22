"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

interface Product {
  name: string
  sku: string
  priceText: string
  unit: string
  description: string
}

export default function SupplierSignUpPage() {
  const router = useRouter()
  const [step, setStep] = useState(1) // 1 = company info, 2 = products
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    industry: "",
    website: "",
    phone: "",
    description: "",
    city: "",
    state: "",
    country: "",
  })
  const [products, setProducts] = useState<Product[]>([
    { name: "", sku: "", priceText: "", unit: "", description: "" }
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNextStep = (e: React.FormEvent) => {
    e.preventDefault()

    // Validation for step 1
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match")
      return
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }

    setError("")
    setStep(2)
  }

  const addProduct = () => {
    setProducts([...products, { name: "", sku: "", priceText: "", unit: "", description: "" }])
  }

  const removeProduct = (index: number) => {
    if (products.length > 1) {
      setProducts(products.filter((_, i) => i !== index))
    }
  }

  const updateProduct = (index: number, field: keyof Product, value: string) => {
    const newProducts = [...products]
    newProducts[index][field] = value
    setProducts(newProducts)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const response = await fetch("/api/auth/register/supplier", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          industry: formData.industry,
          website: formData.website,
          phone: formData.phone,
          description: formData.description,
          city: formData.city,
          state: formData.state,
          country: formData.country,
          products: products.filter(p => p.name && p.priceText), // Only send products with at least name and price
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Registration failed")
      }

      // Redirect to signin page after successful registration
      router.push("/auth/signin?registered=true&type=supplier")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-3 justify-center mb-4">
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
            <h2 className="text-2xl font-bold text-slate-900">Create your supplier account</h2>
            <p className="mt-2 text-sm text-slate-600">
              {step === 1 ? "Step 1 of 2: Company Information" : "Step 2 of 2: Add Your Products"}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleNextStep} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Company Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Your Company"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="you@company.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Industry *
              </label>
              <input
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="e.g., Manufacturing, Technology, Healthcare"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Website *
              </label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="https://yourcompany.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Phone Number *
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="+1 (555) 123-4567"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Tell us about your company and what you supply..."
                rows={3}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password *
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Min. 8 characters"
                required
                minLength={8}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Confirm Password *
              </label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Re-enter password"
                required
                minLength={8}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  City *
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="New York"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  State *
                </label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="NY"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Country *
                </label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                  placeholder="USA"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="hero"
              size="lg"
              className="w-full mt-6"
            >
              Next: Add Products
            </Button>
          </form>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Add Products You Supply</h3>
                <p className="text-sm text-slate-600">Add at least one product. You can add more later.</p>
              </div>

              {products.map((product, index) => (
                <div key={index} className="border-2 border-slate-200 rounded-lg p-4 space-y-3">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-medium text-slate-900">Product {index + 1}</h4>
                    {products.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeProduct(index)}
                        className="text-red-600 text-sm hover:text-red-700"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Product Name *
                    </label>
                    <input
                      type="text"
                      value={product.name}
                      onChange={(e) => updateProduct(index, 'name', e.target.value)}
                      className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
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
                        value={product.sku}
                        onChange={(e) => updateProduct(index, 'sku', e.target.value)}
                        className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                        placeholder="e.g., AL-6061-001"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Unit *
                      </label>
                      <input
                        type="text"
                        value={product.unit}
                        onChange={(e) => updateProduct(index, 'unit', e.target.value)}
                        className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                        placeholder="e.g., per sheet, per lb"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Price *
                    </label>
                    <input
                      type="text"
                      value={product.priceText}
                      onChange={(e) => updateProduct(index, 'priceText', e.target.value)}
                      className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                      placeholder="e.g., $85.00 or $2.50-$3.00"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={product.description}
                      onChange={(e) => updateProduct(index, 'description', e.target.value)}
                      className="w-full px-3 py-2 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                      placeholder="Brief description of the product..."
                      rows={2}
                    />
                  </div>
                </div>
              ))}

              <Button
                type="button"
                onClick={addProduct}
                variant="outline"
                className="w-full"
              >
                + Add Another Product
              </Button>

              <div className="flex gap-3">
                <Button
                  type="button"
                  onClick={() => setStep(1)}
                  variant="outline"
                  className="w-full"
                >
                  Back
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  variant="hero"
                  className="w-full"
                >
                  {loading ? "Creating account..." : "Create Account"}
                </Button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600">
              Already have an account?{" "}
              <Link href="/auth/signin" className="text-blue-600 font-medium hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
