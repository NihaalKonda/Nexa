import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function POST(req: NextRequest) {
  try {
    const { name, email, password, industry, city, state, country } = await req.json()

    // Validation
    if (!name || !email || !password) {
      return NextResponse.json(
        { error: "Name, email, and password are required" },
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

    // Create supplier
    const supplier = await prisma.supplier.create({
      data: {
        name,
        slug,
        contactEmail: email,
        password: hashedPassword,
        industry: industry || null,
        city: city || null,
        state: state || null,
        country: country || null,
      },
      select: {
        id: true,
        name: true,
        contactEmail: true,
        slug: true,
        industry: true,
        city: true,
        state: true,
        country: true,
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
