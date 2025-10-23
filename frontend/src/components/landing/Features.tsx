import { Card } from "@/components/ui/card"
import { Zap, Users, FileText, TrendingUp, Search, FileEdit } from "lucide-react"

const features = [
  {
    icon: Search,
    number: "01",
    title: "Match with Suppliers",
    description: "Our platform uses AI to connects you with qualified suppliers based on your requirements."
  },
  {
    icon: FileEdit,
    number: "02",
    title: "Automated RFPs",
    description: "Generate comprehensive RFPs tailored to your project needs."
  },
  {
    icon: Zap,
    number: "03",
    title: "Close Deals Faster",
    description: "Finalize agreements through end-to-end automated communications."
  },
  {
    icon: FileText,
    number: "04",
    title: "Smart Documentation",
    description: "Automatically organize and manage procurement documents in one centralized platform."
  },
  {
    icon: Users,
    number: "05",
    title: "Direct Connection",
    description: "Connect directly with verified enterprises. No intermediaries, just efficient B2B relationships."
  },
  {
    icon: TrendingUp,
    number: "06",
    title: "Real-time Analytics",
    description: "Get insights into supplier performance, pricing trends, and procurement efficiency metrics."
  }
]

const Features = () => {
  return (
    <section id="features" className="py-24 bg-slate-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Everything You Need for{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Procurement
            </span>
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            From sourcing to deal closure, we've streamlined every step
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="p-8 relative hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-slate-200"
            >
              <div className="w-14 h-14 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 flex items-center justify-center mb-6">
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-2xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-slate-600 leading-relaxed">{feature.description}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Features