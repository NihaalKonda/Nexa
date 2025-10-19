import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import Link from "next/link"

const Hero = () => {
  return (
    <section className="relative min-h-[85vh] flex items-center pt-8 overflow-hidden">
      {/* Background with overlay */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(/hero-bg.jpg)`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50/95 to-white/95" />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Automate Your{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Procurement Process
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto">
            Connect clients and suppliers through intelligent automation.
            Streamline deals, reduce procurement time, and build lasting partnerships.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signup">
              <Button variant="hero" size="lg" className="min-w-[200px] group">
                Start Free Trial
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/search-gpt">
              <Button variant="outline" size="lg" className="min-w-[200px]">
                Watch Demo
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero