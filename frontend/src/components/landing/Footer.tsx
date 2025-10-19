import Image from "next/image"

const Footer = () => {
  return (
    <footer className="bg-slate-50 border-t border-gray-100 py-12">
      <div className="container mx-auto px-6">
        <div className="flex flex-col items-center gap-4">
          <div className="flex items-center gap-2">
            <Image src="/nexa_logo.png" alt="Nexa Logo" width={32} height={32} className="h-8 w-8" />
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Nexa
            </span>
          </div>
          <p className="text-sm text-slate-600">&copy; {new Date().getFullYear()} Nexa. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer