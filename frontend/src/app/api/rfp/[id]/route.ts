import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const rfp = await prisma.rFP.findFirst({
      where: {
        id: params.id,
        companyId: (session.user as any).companyId,
      },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
        shares: true,
      },
    })

    if (!rfp) {
      return NextResponse.json({ error: "RFP not found" }, { status: 404 })
    }

    return NextResponse.json(rfp)
  } catch (error) {
    console.error("RFP fetch error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { title, bodyMd, draftJson, status } = await req.json()

    const rfp = await prisma.rFP.updateMany({
      where: {
        id: params.id,
        companyId: (session.user as any).companyId,
      },
      data: {
        ...(title && { title }),
        ...(bodyMd && { bodyMd }),
        ...(draftJson && { draftJson }),
        ...(status && { status }),
      },
    })

    if (rfp.count === 0) {
      return NextResponse.json({ error: "RFP not found" }, { status: 404 })
    }

    const updated = await prisma.rFP.findUnique({
      where: { id: params.id },
    })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("RFP update error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}
