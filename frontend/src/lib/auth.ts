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

        const company = await prisma.company.findUnique({
          where: {
            email: credentials.email,
          },
        })

        if (!company || !company.password) {
          throw new Error("Invalid credentials")
        }

        const isCorrectPassword = await bcrypt.compare(
          credentials.password,
          company.password
        )

        if (!isCorrectPassword) {
          throw new Error("Invalid credentials")
        }

        return {
          id: company.id,
          email: company.email,
          name: company.name,
          industry: company.industry,
          city: company.city,
          state: company.state,
          country: company.country,
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.email = user.email
        token.name = user.name
        token.industry = (user as any).industry
        token.city = (user as any).city
        token.state = (user as any).state
        token.country = (user as any).country
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id
        ;(session.user as any).companyId = token.id // Company ID is the same as user ID now
        session.user.email = token.email as string
        session.user.name = token.name as string
        ;(session.user as any).industry = token.industry as string | null
        ;(session.user as any).city = token.city as string | null
        ;(session.user as any).state = token.state as string | null
        ;(session.user as any).country = token.country as string | null
      }
      return session
    },
  },
}
