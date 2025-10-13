import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"

// Save a search query
export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { product, location, priceMin, priceMax, resultsCount, results } = await req.json()

    const companyId = (session.user as any).companyId

    // Delete all old search queries for this company (keeping only the new one)
    await prisma.searchQuery.deleteMany({
      where: {
        companyId,
      },
    })

    // Save new search query with complete results
    const searchQuery = await prisma.searchQuery.create({
      data: {
        companyId,
        query: product,
        filtersJson: {
          product,
          location,
          priceMin,
          priceMax,
          results: results || [], // Store the actual supplier results
        },
        resultsCount: resultsCount || 0,
      },
    })

    return NextResponse.json({
      success: true,
      searchQuery,
    })
  } catch (error) {
    console.error("Error saving search query:", error)
    return NextResponse.json(
      { error: "Failed to save search query" },
      { status: 500 }
    )
  }
}

// Get last search query for the current company
export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const companyId = (session.user as any).companyId

    // Get the most recent search query
    const lastSearchQuery = await prisma.searchQuery.findFirst({
      where: {
        companyId,
      },
      orderBy: {
        createdAt: "desc",
      },
    })

    if (!lastSearchQuery) {
      return NextResponse.json({
        success: true,
        searchQuery: null,
      })
    }

    return NextResponse.json({
      success: true,
      searchQuery: {
        id: lastSearchQuery.id,
        query: lastSearchQuery.query,
        filters: lastSearchQuery.filtersJson,
        resultsCount: lastSearchQuery.resultsCount,
        createdAt: lastSearchQuery.createdAt,
      },
    })
  } catch (error) {
    console.error("Error fetching last search query:", error)
    return NextResponse.json(
      { error: "Failed to fetch last search query" },
      { status: 500 }
    )
  }
}
