"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"
import { Building2, Factory } from "lucide-react"

export default function SignupRoleSelection() {
  const router = useRouter()
  const [selectedRole, setSelectedRole] = useState<"buyer" | "supplier" | null>(null)

  const handleContinue = () => {
    if (selectedRole === "buyer") {
      router.push("/auth/signup/buyer")
    } else if (selectedRole === "supplier") {
      router.push("/auth/signup/supplier")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col">
      {/* Header */}
      <header className="w-full bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="container mx-auto px-6 py-4">
          <Link href="/" className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity w-fit">
            <Image
              src="/nexa_logo.png"
              alt="Nexa Logo"
              width={32}
              height={32}
              className="h-8 w-8"
            />
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Nexa
            </span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-4xl">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
              Welcome to Nexa
            </h1>
            <p className="text-lg text-slate-600">
              Let's get started! Are you a buyer or a supplier?
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Buyer Card */}
            <button
              onClick={() => setSelectedRole("buyer")}
              className={`bg-white rounded-2xl p-8 border-2 transition-all duration-300 text-left hover:shadow-xl ${
                selectedRole === "buyer"
                  ? "border-blue-500 shadow-lg ring-4 ring-blue-100"
                  : "border-slate-200 hover:border-blue-300"
              }`}
            >
              <div className="flex items-start gap-4 mb-4">
                <div className={`p-3 rounded-xl ${selectedRole === "buyer" ? "bg-blue-100" : "bg-slate-100"}`}>
                  <Building2 className={`w-8 h-8 ${selectedRole === "buyer" ? "text-blue-600" : "text-slate-600"}`} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">I'm a Buyer</h3>
                  <div className={`w-12 h-1 rounded ${selectedRole === "buyer" ? "bg-blue-600" : "bg-slate-300"}`} />
                </div>
              </div>
              <p className="text-slate-600 mb-4">
                I'm looking to find and connect with suppliers for my business needs.
              </p>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">✓</span>
                  <span>Search and discover suppliers</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">✓</span>
                  <span>Generate automated RFPs</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">✓</span>
                  <span>Manage procurement process</span>
                </li>
              </ul>
            </button>

            {/* Supplier Card */}
            <button
              onClick={() => setSelectedRole("supplier")}
              className={`bg-white rounded-2xl p-8 border-2 transition-all duration-300 text-left hover:shadow-xl ${
                selectedRole === "supplier"
                  ? "border-cyan-500 shadow-lg ring-4 ring-cyan-100"
                  : "border-slate-200 hover:border-cyan-300"
              }`}
            >
              <div className="flex items-start gap-4 mb-4">
                <div className={`p-3 rounded-xl ${selectedRole === "supplier" ? "bg-cyan-100" : "bg-slate-100"}`}>
                  <Factory className={`w-8 h-8 ${selectedRole === "supplier" ? "text-cyan-600" : "text-slate-600"}`} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">I'm a Supplier</h3>
                  <div className={`w-12 h-1 rounded ${selectedRole === "supplier" ? "bg-cyan-600" : "bg-slate-300"}`} />
                </div>
              </div>
              <p className="text-slate-600 mb-4">
                I want to showcase my products and receive business opportunities.
              </p>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-start gap-2">
                  <span className="text-cyan-600 mt-0.5">✓</span>
                  <span>List your products and services</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-600 mt-0.5">✓</span>
                  <span>Receive targeted RFPs</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-600 mt-0.5">✓</span>
                  <span>Connect with potential buyers</span>
                </li>
              </ul>
            </button>
          </div>

          {/* Continue Button */}
          <div className="text-center">
            <Button
              onClick={handleContinue}
              disabled={!selectedRole}
              variant="hero"
              size="lg"
              className="min-w-[250px] text-lg px-8 py-6 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue as {selectedRole === "buyer" ? "Buyer" : selectedRole === "supplier" ? "Supplier" : "..."}
            </Button>
            <p className="mt-6 text-slate-600">
              Already have an account?{" "}
              <Link href="/auth/signin" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
