import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { redirect } from "next/navigation"
import Link from "next/link"

export default async function DashboardPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect("/auth/signin")
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Welcome to Nexa</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/dashboard/search"
            className="p-6 border rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-xl font-semibold mb-2">Product Search</h2>
            <p className="text-gray-600">
              Search for industrial products and suppliers
            </p>
          </Link>

          <Link
            href="/dashboard/rfp/new"
            className="p-6 border rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-xl font-semibold mb-2">Create RFP</h2>
            <p className="text-gray-600">
              Generate a new RFP with AI assistance
            </p>
          </Link>

          <Link
            href="/dashboard/settings"
            className="p-6 border rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-xl font-semibold mb-2">Settings</h2>
            <p className="text-gray-600">
              Manage your company and user settings
            </p>
          </Link>
        </div>
      </div>
    </div>
  )
}
