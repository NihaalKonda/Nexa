import { NextRequest, NextResponse } from "next/server"

// Use server-side env variable (without NEXT_PUBLIC prefix for API routes)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || "http://localhost:5001"

export async function POST(req: NextRequest) {
  try {
    const { product, location, price_min, price_max, useDetailed } = await req.json()

    console.log("Combined search request:", { product, location, price_min, price_max, useDetailed })
    console.log("API_BASE_URL constant value:", API_BASE_URL)
    console.log("process.env.NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL)
    console.log("process.env.API_URL:", process.env.API_URL)

    if (!product) {
      return NextResponse.json(
        { error: "Product search term is required" },
        { status: 400 }
      )
    }

    // Get base URL for internal API call
    const protocol = req.headers.get('x-forwarded-proto') || 'http'
    const host = req.headers.get('host') || 'localhost:3000'
    const baseUrl = `${protocol}://${host}`

    const gptSearchUrl = `${API_BASE_URL}/api/search${useDetailed ? '/detailed' : ''}`
    console.log("Calling internal search at:", `${baseUrl}/api/search/internal`)
    console.log("Calling GPT search at:", gptSearchUrl)

    // Execute both searches in parallel
    const [internalResponse, gptResponse] = await Promise.all([
      // Internal database search
      fetch(`${baseUrl}/api/search/internal`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ product, location, price_min, price_max, useDetailed }),
      }),
      // GPT search (existing Flask backend)
      fetch(`${API_BASE_URL}/api/search${useDetailed ? '/detailed' : ''}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ product, location, price_min, price_max }),
      }),
    ])

    // Parse responses with error handling
    let internalData = { success: false, suppliers: [] }
    let gptData = { suppliers: [] }

    try {
      if (internalResponse.ok) {
        internalData = await internalResponse.json()
        console.log("Internal search successful, found:", internalData.suppliers?.length || 0, "suppliers")
      } else {
        const errorText = await internalResponse.text()
        console.error("Internal search failed with status:", internalResponse.status, errorText)
      }
    } catch (err) {
      console.error("Error parsing internal response:", err)
    }

    try {
      if (gptResponse.ok) {
        gptData = await gptResponse.json()
        console.log("GPT search successful, found:", gptData.suppliers?.length || 0, "suppliers")
      } else {
        const errorText = await gptResponse.text()
        console.error("GPT search failed with status:", gptResponse.status, errorText)
      }
    } catch (err) {
      console.error("Error parsing GPT response:", err)
    }

    // Combine results
    let combinedSuppliers = []

    // Add internal suppliers first (they're from our verified database)
    if (internalData.success && internalData.suppliers) {
      combinedSuppliers = internalData.suppliers.map((s: any) => ({
        ...s,
        source: "internal",
        // Boost score for internal suppliers
        score: s.score || 90,
      }))
    }

    // Add GPT suppliers
    if (gptData.suppliers && Array.isArray(gptData.suppliers)) {
      const gptSuppliers = gptData.suppliers.map((s: any) => ({
        ...s,
        source: "gpt",
      }))

      // Merge suppliers, avoiding duplicates based on name similarity
      gptSuppliers.forEach((gptSupplier: any) => {
        const isDuplicate = combinedSuppliers.some((existing: any) => {
          const nameSimilar =
            existing.name.toLowerCase().includes(gptSupplier.name.toLowerCase()) ||
            gptSupplier.name.toLowerCase().includes(existing.name.toLowerCase())

          const websiteSame =
            existing.website && gptSupplier.website &&
            existing.website !== "N/A" && gptSupplier.website !== "N/A" &&
            existing.website.toLowerCase() === gptSupplier.website.toLowerCase()

          return nameSimilar || websiteSame
        })

        if (!isDuplicate) {
          combinedSuppliers.push(gptSupplier)
        }
      })
    }

    // Sort by score (internal suppliers with higher scores will appear first)
    combinedSuppliers.sort((a: any, b: any) => (b.score || 0) - (a.score || 0))

    console.log("Combined search complete. Total suppliers:", combinedSuppliers.length)

    return NextResponse.json({
      success: true,
      suppliers: combinedSuppliers,
      count: combinedSuppliers.length,
      internalCount: internalData.suppliers?.length || 0,
      gptCount: gptData.suppliers?.length || 0,
    })
  } catch (error) {
    console.error("Combined search error (caught):", error)
    console.error("Stack trace:", error instanceof Error ? error.stack : "No stack trace")
    return NextResponse.json(
      { error: "Failed to perform combined search", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
