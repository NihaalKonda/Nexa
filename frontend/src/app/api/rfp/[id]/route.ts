import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params
    const { searchParams } = new URL(req.url)
    const format = searchParams.get('format') || 'pdf'

    // Check user role to determine access permissions
    const userRole = (session.user as any).role

    // Build where clause based on role
    const whereClause: any = { id }

    if (userRole === 'supplier') {
      // Suppliers can only view RFPs generated for them
      whereClause.supplierId = (session.user as any).supplierId
    } else {
      // Buyers can only view their own RFPs
      whereClause.companyId = (session.user as any).companyId
    }

    const rfp = await prisma.rFP.findFirst({
      where: whereClause,
      include: {
        company: {
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

    // If requesting PDF, serve the PDF content
    if (format === 'pdf' && rfp.pdfContent) {
      return new NextResponse(Buffer.from(rfp.pdfContent), {
        headers: {
          "Content-Type": "application/pdf",
          "Content-Disposition": `inline; filename="${rfp.filename || 'rfp.pdf'}"`,
        },
      })
    }

    // If requesting HTML, serve the HTML content
    if (format === 'html' && rfp.htmlContent) {
      return new NextResponse(rfp.htmlContent, {
        headers: {
          "Content-Type": "text/html",
          "Content-Disposition": "inline",
        },
      })
    }

    // Default: return JSON
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
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { id } = await params
    const { title, bodyMd, draftJson, status } = await req.json()

    // Prepare update data
    const updateData: any = {}
    if (title) updateData.title = title
    if (bodyMd !== undefined) updateData.bodyMd = bodyMd
    if (draftJson) updateData.draftJson = draftJson
    if (status) updateData.status = status

    // If bodyMd is being updated, regenerate PDF
    if (bodyMd !== undefined) {
      try {
        // Call Python backend to regenerate PDF from markdown
        const pdfResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'}/api/rfp/regenerate-pdf`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ markdown: bodyMd }),
        })

        if (pdfResponse.ok) {
          const pdfData = await pdfResponse.json()
          if (pdfData.pdf_content) {
            updateData.pdfContent = Buffer.from(pdfData.pdf_content, 'base64')
          }
        }
      } catch (pdfError) {
        console.error("PDF regeneration error:", pdfError)
        // Continue with update even if PDF regeneration fails
      }
    }

    const rfp = await prisma.rFP.updateMany({
      where: {
        id,
        companyId: (session.user as any).companyId,
      },
      data: updateData,
    })

    if (rfp.count === 0) {
      return NextResponse.json({ error: "RFP not found" }, { status: 404 })
    }

    const updated = await prisma.rFP.findUnique({
      where: { id },
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
