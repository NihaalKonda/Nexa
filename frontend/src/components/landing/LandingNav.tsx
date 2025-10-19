import { Button } from "@/components/ui/button"
import Image from "next/image"
import Link from "next/link"

const LandingNav = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
          >
            <Image src="/nexa_logo.png" alt="Nexa Logo" width={40} height={40} className="h-10 w-10" />
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Nexa
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link href="/auth/signin">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/auth/signup">
              <Button variant="hero">Get Started</Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default LandingNav