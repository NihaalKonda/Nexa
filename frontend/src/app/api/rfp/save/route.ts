import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { markdown, filename, htmlContent, pdfContent, title, supplierId, supplierName } = body

    // Get company ID from session
    const companyId = (session.user as any).companyId

    if (!companyId) {
      return NextResponse.json({ error: "Company ID not found" }, { status: 400 })
    }

    // Create RFP record in database
    const rfp = await prisma.rFP.create({
      data: {
        companyId,
        title: title || "Generated RFP",
        bodyMd: markdown,
        filename: filename,
        htmlContent: htmlContent,
        pdfContent: pdfContent ? Buffer.from(pdfContent, 'base64') : null,
        draftJson: {}, // Empty for now, can be populated later
        status: "draft",
        supplierId: supplierId || null,
        supplierName: supplierName || null,
      },
    })

    return NextResponse.json({
      success: true,
      rfpId: rfp.id,
      filename: rfp.filename,
    })
  } catch (error) {
    console.error("Error saving RFP:", error)
    return NextResponse.json(
      { error: "Failed to save RFP to database" },
      { status: 500 }
    )
  }
}
