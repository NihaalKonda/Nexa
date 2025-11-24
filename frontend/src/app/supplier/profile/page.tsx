"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"

export default function SupplierProfile() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isSaving, setIsSaving] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    contactEmail: "",
    industry: "",
    website: "",
    contactPhone: "",
    description: "",
    address: "",
    city: "",
    state: "",
    country: "",
  })

  // Redirect if not authenticated or not a supplier
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin")
    } else if (status === "authenticated" && (session?.user as any)?.role !== "supplier") {
      router.push("/supplier-search")
    }
  }, [status, session, router])

  // Load supplier data from database
  useEffect(() => {
    const fetchSupplierData = async () => {
      if (status === "authenticated") {
        try {
          const response = await fetch("/api/supplier/profile")
          if (response.ok) {
            const data = await response.json()
            const supplier = data.supplier
            setFormData({
              name: supplier.name || "",
              contactEmail: supplier.contactEmail || "",
              industry: supplier.industry || "",
              website: supplier.website || "",
              contactPhone: supplier.contactPhone || "",
              description: supplier.description || "",
              address: supplier.address || "",
              city: supplier.city || "",
              state: supplier.state || "",
              country: supplier.country || "",
            })
          }
        } catch (err) {
          console.error("Error loading supplier data:", err)
        }
      }
    }

    fetchSupplierData()
  }, [status])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError("")
    setSuccess("")

    try {
      console.log("Submitting form data:", formData)

      const response = await fetch("/api/supplier/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()
      console.log("Response:", response.status, data)

      if (!response.ok) {
        throw new Error(data.error || "Failed to update profile")
      }

      setSuccess("Profile updated successfully!")
      // Refresh the session to get updated data after a brief delay to show the success message
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } catch (err: any) {
      console.error("Error updating profile:", err)
      setError(err.message || "Failed to update profile")
    } finally {
      setIsSaving(false)
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
                onClick={() => router.push("/supplier/rfps")}
                variant="ghost"
                className="text-sm px-4 py-2"
              >
                RFPs
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
                  onClick={() => {
                    router.push("/supplier/rfps")
                    setMobileMenuOpen(false)
                  }}
                  variant="ghost"
                  className="justify-start text-sm px-4 py-2"
                >
                  RFPs
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
                Supplier Profile
              </h1>
              <p className="text-slate-600 mt-2">
                Manage your company information and details that buyers will see.
              </p>
            </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 text-sm">{success}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Company Name */}
            <div>
              <label htmlFor="name" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Company Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Contact Email */}
            <div>
              <label htmlFor="contactEmail" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Contact Email *
              </label>
              <input
                type="email"
                id="contactEmail"
                name="contactEmail"
                value={formData.contactEmail}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Industry */}
            <div>
              <label htmlFor="industry" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Industry *
              </label>
              <input
                type="text"
                id="industry"
                name="industry"
                value={formData.industry}
                onChange={handleInputChange}
                required
                placeholder="e.g., Manufacturing, Technology, Healthcare"
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Website */}
            <div>
              <label htmlFor="website" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Website *
              </label>
              <input
                type="url"
                id="website"
                name="website"
                value={formData.website}
                onChange={handleInputChange}
                required
                placeholder="https://example.com"
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Contact Phone */}
            <div>
              <label htmlFor="contactPhone" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Contact Phone *
              </label>
              <input
                type="tel"
                id="contactPhone"
                name="contactPhone"
                value={formData.contactPhone}
                onChange={handleInputChange}
                required
                placeholder="+1 (555) 123-4567"
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Company Description *
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                rows={4}
                placeholder="Tell buyers about your company, products, and services..."
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Location */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="city" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                  City *
                </label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label htmlFor="state" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                  State/Province *
                </label>
                <input
                  type="text"
                  id="state"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label htmlFor="country" className="block text-xs md:text-sm font-medium text-slate-700 mb-1 md:mb-2">
                Country *
              </label>
              <input
                type="text"
                id="country"
                name="country"
                value={formData.country}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 md:px-4 md:py-3 text-sm md:text-base border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
              />
            </div>

            {/* Submit Button */}
            <div className="flex flex-col md:flex-row justify-end gap-3 md:gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/")}
                className="w-full md:w-auto text-sm md:text-base"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSaving}
                variant="hero"
                size="lg"
                className="w-full md:w-auto text-sm md:text-base hover:shadow-md hover:scale-[1.02] transition-transform"
              >
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
          </div>
        </div>
      </main>
    </div>
  )
}
