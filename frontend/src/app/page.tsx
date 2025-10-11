import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Nexa</h1>
          <nav className="flex gap-4">
            <Link href="/pricing" className="text-sm hover:underline">
              Pricing
            </Link>
            <Link href="/auth/signin" className="text-sm hover:underline">
              Sign In
            </Link>
            <Link
              href="/auth/signup"
              className="text-sm bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="max-w-4xl text-center space-y-6">
          <h1 className="text-5xl font-bold tracking-tight">
            Industrial Procurement, Powered by AI
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover verified suppliers, search technical specifications, and
            generate professional RFPs in minutes—not days.
          </p>
          <div className="flex gap-4 justify-center pt-4">
            <Link
              href="/auth/signup"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-blue-700"
            >
              Start Free Trial
            </Link>
            <Link
              href="/dashboard/search"
              className="border border-gray-300 px-6 py-3 rounded-lg text-lg font-medium hover:bg-gray-50"
            >
              View Demo
            </Link>
          </div>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
          <div className="p-6 border rounded-lg">
            <h3 className="text-xl font-semibold mb-2">Smart Search</h3>
            <p className="text-gray-600">
              Search across thousands of products with intelligent filtering by specs,
              certifications, and suppliers.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="text-xl font-semibold mb-2">AI RFP Generation</h3>
            <p className="text-gray-600">
              Generate professional RFPs tailored to your requirements in seconds
              with AI assistance.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="text-xl font-semibold mb-2">Verified Suppliers</h3>
            <p className="text-gray-600">
              Access a curated network of industrial suppliers with verified
              credentials and reviews.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t mt-16">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-gray-600">
          <p>&copy; 2025 Nexa. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
