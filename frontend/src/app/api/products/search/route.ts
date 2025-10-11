import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { query, filters, page = 1, limit = 20 } = await req.json()

    // Build the where clause based on filters
    const where: any = {}

    if (query) {
      where.OR = [
        { name: { contains: query, mode: "insensitive" } },
        { sku: { contains: query, mode: "insensitive" } },
        { mpn: { contains: query, mode: "insensitive" } },
      ]
    }

    if (filters?.supplierId) {
      where.supplierId = filters.supplierId
    }

    // Get products with pagination and include supplier info
    const [products, total] = await Promise.all([
      prisma.product.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        include: {
          supplier: {
            select: {
              id: true,
              name: true,
              verified: true,
              rating: true,
              country: true,
            },
          },
        },
        orderBy: [
          { score: "desc" },
          { createdAt: "desc" },
        ],
      }),
      prisma.product.count({ where }),
    ])

    // Log the search query
    await prisma.searchQuery.create({
      data: {
        companyId: (session.user as any).companyId,
        query: query || "",
        filtersJson: filters || {},
        resultsCount: total,
      },
    })

    return NextResponse.json({
      products,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    })
  } catch (error) {
    console.error("Product search error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}
