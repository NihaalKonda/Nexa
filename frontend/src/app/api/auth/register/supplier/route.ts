import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function POST(req: NextRequest) {
  try {
    const { name, email, password, industry, website, phone, description, city, state, country, products } = await req.json()

    // Validation
    if (!name || !email || !password || !industry || !website || !phone || !description || !city || !state || !country) {
      return NextResponse.json(
        { error: "All fields are required" },
        { status: 400 }
      )
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters" },
        { status: 400 }
      )
    }

    // Check if supplier already exists
    const existingSupplier = await prisma.supplier.findUnique({
      where: { contactEmail: email },
    })

    if (existingSupplier) {
      return NextResponse.json(
        { error: "A supplier with this email already exists" },
        { status: 400 }
      )
    }

    // Generate slug from company name
    const baseSlug = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")

    // Ensure slug is unique
    let slug = baseSlug
    let counter = 1
    while (await prisma.supplier.findUnique({ where: { slug } })) {
      slug = `${baseSlug}-${counter}`
      counter++
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 12)

    // Create supplier with products
    const supplier = await prisma.supplier.create({
      data: {
        name,
        slug,
        contactEmail: email,
        password: hashedPassword,
        industry,
        website,
        contactPhone: phone,
        description,
        city,
        state,
        country,
        products: products && products.length > 0 ? {
          create: products.map((p: any) => ({
            name: p.name,
            sku: p.sku || null,
            priceText: p.priceText,
            unit: p.unit,
            description: p.description || null,
          }))
        } : undefined,
      },
      select: {
        id: true,
        name: true,
        contactEmail: true,
        slug: true,
        industry: true,
        website: true,
        contactPhone: true,
        description: true,
        city: true,
        state: true,
        country: true,
        products: true,
        createdAt: true,
      },
    })

    return NextResponse.json(
      {
        success: true,
        supplier,
        message: "Supplier registered successfully",
      },
      { status: 201 }
    )
  } catch (error) {
    console.error("Supplier registration error:", error)
    return NextResponse.json(
      { error: "Failed to register supplier" },
      { status: 500 }
    )
  }
}
