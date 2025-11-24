import { NextAuthOptions } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { prisma } from "./db"
import bcrypt from "bcryptjs"

export const authOptions: NextAuthOptions = {
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/auth/signin",
  },
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Invalid credentials")
        }

        // First, try to find a buyer (Company)
        const company = await prisma.company.findUnique({
          where: {
            email: credentials.email,
          },
        })

        if (company && company.password) {
          const isCorrectPassword = await bcrypt.compare(
            credentials.password,
            company.password
          )

          if (isCorrectPassword) {
            return {
              id: company.id,
              email: company.email,
              name: company.name,
              industry: company.industry,
              city: company.city,
              state: company.state,
              country: company.country,
              role: "buyer",
            }
          }
        }

        // If not a company, try to find a supplier
        const supplier = await prisma.supplier.findUnique({
          where: {
            contactEmail: credentials.email,
          },
        })

        if (supplier && supplier.password) {
          const isCorrectPassword = await bcrypt.compare(
            credentials.password,
            supplier.password
          )

          if (isCorrectPassword) {
            return {
              id: supplier.id,
              email: supplier.contactEmail,
              name: supplier.name,
              industry: supplier.industry,
              city: supplier.city,
              state: supplier.state,
              country: supplier.country,
              role: "supplier",
              website: supplier.website,
              contactPhone: supplier.contactPhone,
              description: supplier.description,
            }
          }
        }

        throw new Error("Invalid credentials")
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.email = user.email
        token.name = user.name
        token.role = (user as any).role
        token.industry = (user as any).industry
        token.city = (user as any).city
        token.state = (user as any).state
        token.country = (user as any).country
        token.website = (user as any).website
        token.contactPhone = (user as any).contactPhone
        token.description = (user as any).description
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id
        ;(session.user as any).role = token.role as "buyer" | "supplier"
        ;(session.user as any).companyId = token.role === "buyer" ? token.id : null
        ;(session.user as any).supplierId = token.role === "supplier" ? token.id : null
        session.user.email = token.email as string
        session.user.name = token.name as string
        ;(session.user as any).industry = token.industry as string | null
        ;(session.user as any).city = token.city as string | null
        ;(session.user as any).state = token.state as string | null
        ;(session.user as any).country = token.country as string | null
        ;(session.user as any).website = token.website as string | null
        ;(session.user as any).contactPhone = token.contactPhone as string | null
        ;(session.user as any).description = token.description as string | null
      }
      return session
    },
  },
}
