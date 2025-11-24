import { NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can view their products" }, { status: 403 })
    }

    const product = await prisma.product.findUnique({
      where: {
        id: params.id,
      },
    })

    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 })
    }

    // Verify product belongs to this supplier
    if (product.supplierId !== user.supplierId) {
      return NextResponse.json({ error: "You don't have access to this product" }, { status: 403 })
    }

    return NextResponse.json({ product })
  } catch (error: any) {
    console.error("Error fetching product:", error)
    return NextResponse.json(
      { error: error.message || "Failed to fetch product" },
      { status: 500 }
    )
  }
}

export async function PUT(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can update products" }, { status: 403 })
    }

    // Verify product exists and belongs to this supplier
    const existingProduct = await prisma.product.findUnique({
      where: { id: params.id },
    })

    if (!existingProduct) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 })
    }

    if (existingProduct.supplierId !== user.supplierId) {
      return NextResponse.json({ error: "You don't have access to this product" }, { status: 403 })
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

    // Update product
    const product = await prisma.product.update({
      where: { id: params.id },
      data: {
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
    console.error("Error updating product:", error)
    return NextResponse.json(
      { error: error.message || "Failed to update product" },
      { status: 500 }
    )
  }
}

export async function DELETE(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const user = session.user as any
    if (user.role !== "supplier") {
      return NextResponse.json({ error: "Only suppliers can delete products" }, { status: 403 })
    }

    // Verify product exists and belongs to this supplier
    const existingProduct = await prisma.product.findUnique({
      where: { id: params.id },
    })

    if (!existingProduct) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 })
    }

    if (existingProduct.supplierId !== user.supplierId) {
      return NextResponse.json({ error: "You don't have access to this product" }, { status: 403 })
    }

    // Delete product
    await prisma.product.delete({
      where: { id: params.id },
    })

    return NextResponse.json({
      success: true,
    })
  } catch (error: any) {
    console.error("Error deleting product:", error)
    return NextResponse.json(
      { error: error.message || "Failed to delete product" },
      { status: 500 }
    )
  }
}
