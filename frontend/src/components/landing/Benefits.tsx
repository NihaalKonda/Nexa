import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Building2, Package } from "lucide-react"
import Link from "next/link"

const Benefits = () => {
  return (
    <section id="benefits" className="py-24 bg-white">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Built for{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Both Sides
            </span>
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Whether you're sourcing or supplying, Nexa has you covered
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <Card className="p-10 border-2 border-blue-200 hover:border-blue-400 transition-colors bg-gradient-to-br from-white to-blue-50">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 flex items-center justify-center mb-6">
              <Building2 className="w-8 h-8 text-white" />
            </div>

            <h3 className="text-2xl font-bold mb-4">For Buyers</h3>

            <ul className="space-y-4 mb-8">
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-blue-600" />
                </div>
                <span className="text-slate-600">Reduce procurement cycle time</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-blue-600" />
                </div>
                <span className="text-slate-600">Access vetted suppliers</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-blue-600" />
                </div>
                <span className="text-slate-600">Automated RFP generation and management</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-blue-600" />
                </div>
                <span className="text-slate-600">Handle client communications</span>
              </li>
            </ul>

            <Link href="/auth/signup/buyer">
              <Button variant="hero" className="w-full" size="lg">
                Start Sourcing
              </Button>
            </Link>
          </Card>

          <Card className="p-10 border-2 border-cyan-200 hover:border-cyan-400 transition-colors bg-gradient-to-br from-white to-cyan-50">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 flex items-center justify-center mb-6">
              <Package className="w-8 h-8 text-white" />
            </div>

            <h3 className="text-2xl font-bold mb-4">For Suppliers</h3>

            <ul className="space-y-4 mb-8">
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-cyan-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-cyan-500" />
                </div>
                <span className="text-slate-600">Direct access to qualified buyers</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-cyan-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-cyan-500" />
                </div>
                <span className="text-slate-600">Automated proposal response tools</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-cyan-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-cyan-500" />
                </div>
                <span className="text-slate-600">Real-time tracking and analytics</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-cyan-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-cyan-500" />
                </div>
                <span className="text-slate-600">Build long-term client relationships</span>
              </li>
            </ul>

            <Link href="/auth/signup/supplier">
              <Button variant="outline" className="w-full" size="lg">
                Join as Supplier
              </Button>
            </Link>
          </Card>
        </div>
      </div>
    </section>
  )
}

export default Benefits
