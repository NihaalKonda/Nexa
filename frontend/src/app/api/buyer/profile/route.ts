import { NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function PUT(req: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "buyer") {
      return NextResponse.json({ error: "Only buyers can update their profile" }, { status: 403 })
    }

    if (!user.companyId) {
      return NextResponse.json({ error: "Company ID not found in session" }, { status: 400 })
    }

    const body = await req.json()
    const {
      name,
      email,
      industry,
      city,
      state,
      country,
    } = body

    console.log("Updating company with ID:", user.companyId)
    console.log("Update data:", { name, email, industry, city, state, country })

    // Get current company to check if email changed
    const currentCompany = await prisma.company.findUnique({
      where: { id: user.companyId },
      select: { email: true }
    })

    if (!currentCompany) {
      return NextResponse.json({ error: "Company not found" }, { status: 404 })
    }

    // Check if email is being changed and if it already exists
    if (email && email !== currentCompany.email) {
      const existingCompany = await prisma.company.findFirst({
        where: {
          email,
          id: { not: user.companyId }
        }
      })

      if (existingCompany) {
        return NextResponse.json({ error: "This email is already in use by another company" }, { status: 400 })
      }
    }

    // Update company in database
    const updatedCompany = await prisma.company.update({
      where: {
        id: user.companyId,
      },
      data: {
        name,
        email,
        industry,
        city,
        state,
        country,
      },
    })

    console.log("Company updated successfully:", updatedCompany.id)

    return NextResponse.json({
      success: true,
      company: updatedCompany,
    })
  } catch (error: any) {
    console.error("Error updating company profile:", error)
    console.error("Error details:", {
      message: error.message,
      code: error.code,
      meta: error.meta
    })
    return NextResponse.json(
      { error: error.message || "Failed to update profile" },
      { status: 500 }
    )
  }
}

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "buyer") {
      return NextResponse.json({ error: "Only buyers can view their profile" }, { status: 403 })
    }

    const company = await prisma.company.findUnique({
      where: {
        id: user.companyId,
      },
    })

    if (!company) {
      return NextResponse.json({ error: "Company not found" }, { status: 404 })
    }

    return NextResponse.json({ company })
  } catch (error: any) {
    console.error("Error fetching company profile:", error)
    return NextResponse.json(
      { error: error.message || "Failed to fetch profile" },
      { status: 500 }
    )
  }
}
