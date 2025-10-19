import LandingNav from "@/components/landing/LandingNav"
import Hero from "@/components/landing/Hero"
import Features from "@/components/landing/Features"
import Benefits from "@/components/landing/Benefits"
import CTA from "@/components/landing/CTA"
import Footer from "@/components/landing/Footer"

export default function Home() {
  return (
    <div className="min-h-screen">
      <LandingNav />
      <main>
        <Hero />
        <Features />
        <Benefits />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}