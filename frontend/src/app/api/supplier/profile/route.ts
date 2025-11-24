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
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can update their profile" }, { status: 403 })
    }

    if (!user.supplierId) {
      return NextResponse.json({ error: "Supplier ID not found in session" }, { status: 400 })
    }

    const body = await req.json()
    const {
      name,
      contactEmail,
      industry,
      website,
      contactPhone,
      description,
      address,
      city,
      state,
      country,
    } = body

    console.log("Updating supplier with ID:", user.supplierId)
    console.log("Update data:", { name, contactEmail, industry, website, contactPhone, description, city, state, country })

    // Get current supplier to check if name or email changed
    const currentSupplier = await prisma.supplier.findUnique({
      where: { id: user.supplierId },
      select: { name: true, slug: true, contactEmail: true }
    })

    if (!currentSupplier) {
      return NextResponse.json({ error: "Supplier not found" }, { status: 404 })
    }

    // Check if contactEmail is being changed and if it already exists
    if (contactEmail && contactEmail !== currentSupplier.contactEmail) {
      const existingSupplier = await prisma.supplier.findFirst({
        where: {
          contactEmail,
          id: { not: user.supplierId }
        }
      })

      if (existingSupplier) {
        return NextResponse.json({ error: "This email is already in use by another supplier" }, { status: 400 })
      }
    }

    // Generate slug from name only if name changed
    let slug = currentSupplier.slug
    if (name && name !== currentSupplier.name) {
      const baseSlug = name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')

      // Add timestamp to ensure uniqueness if slug changed
      slug = `${baseSlug}-${Date.now()}`
    }

    // Update supplier in database
    const updatedSupplier = await prisma.supplier.update({
      where: {
        id: user.supplierId,
      },
      data: {
        name,
        slug,
        contactEmail,
        industry,
        website,
        contactPhone,
        description,
        address,
        city,
        state,
        country,
      },
    })

    console.log("Supplier updated successfully:", updatedSupplier.id)

    return NextResponse.json({
      success: true,
      supplier: updatedSupplier,
    })
  } catch (error: any) {
    console.error("Error updating supplier profile:", error)
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
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can view their profile" }, { status: 403 })
    }

    const supplier = await prisma.supplier.findUnique({
      where: {
        id: user.supplierId,
      },
      include: {
        products: true,
      },
    })

    if (!supplier) {
      return NextResponse.json({ error: "Supplier not found" }, { status: 404 })
    }

    return NextResponse.json({ supplier })
  } catch (error: any) {
    console.error("Error fetching supplier profile:", error)
    return NextResponse.json(
      { error: error.message || "Failed to fetch profile" },
      { status: 500 }
    )
  }
}
