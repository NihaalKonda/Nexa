import { NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can view their products" }, { status: 403 })
    }

    const products = await prisma.product.findMany({
      where: {
        supplierId: user.supplierId,
      },
      orderBy: {
        createdAt: "desc",
      },
    })

    return NextResponse.json({ products })
  } catch (error: any) {
    console.error("Error fetching products:", error)
    return NextResponse.json(
      { error: error.message || "Failed to fetch products" },
      { status: 500 }
    )
  }
}

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can create products" }, { status: 403 })
    }

    if (!user.supplierId) {
      return NextResponse.json({ error: "Supplier ID not found in session" }, { status: 400 })
    }

    const body = await req.json()
    const {
      name,
      sku,
      mpn,
      priceText,
      currency,
      unit,
      description,
      imageUrl,
      inStock,
      specsJson,
      certificationsJson,
    } = body

    // Validate required fields
    if (!name) {
      return NextResponse.json({ error: "Product name is required" }, { status: 400 })
    }

    // Create product
    const product = await prisma.product.create({
      data: {
        supplierId: user.supplierId,
        name,
        sku: sku || null,
        mpn: mpn || null,
        priceText: priceText || null,
        currency: currency || null,
        unit: unit || null,
        description: description || null,
        imageUrl: imageUrl || null,
        inStock: inStock !== undefined ? inStock : true,
        specsJson: specsJson || null,
        certificationsJson: certificationsJson || null,
      },
    })

    return NextResponse.json({
      success: true,
      product,
    })
  } catch (error: any) {
    console.error("Error creating product:", error)
    return NextResponse.json(
      { error: error.message || "Failed to create product" },
      { status: 500 }
    )
  }
}
