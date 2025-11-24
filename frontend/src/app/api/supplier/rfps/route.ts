import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get supplier ID from session
    const supplierId = (session.user as any).supplierId

    if (!supplierId) {
      return NextResponse.json({ error: "Supplier ID not found" }, { status: 400 })
    }

    // Fetch all RFPs for this supplier
    const rfps = await prisma.rFP.findMany({
      where: {
        supplierId: supplierId,
      },
      select: {
        id: true,
        title: true,
        supplierName: true,
        status: true,
        createdAt: true,
        updatedAt: true,
        company: {
          select: {
            name: true,
            email: true,
            city: true,
            state: true,
            country: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    })

    return NextResponse.json({
      success: true,
      rfps,
      count: rfps.length,
    })
  } catch (error) {
    console.error("Error fetching supplier RFPs:", error)
    return NextResponse.json(
      { error: "Failed to fetch RFPs" },
      { status: 500 }
    )
  }
}
