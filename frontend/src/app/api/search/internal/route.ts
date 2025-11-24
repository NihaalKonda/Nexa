import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"

export async function POST(req: NextRequest) {
  try {
    const { product, location, price_min, price_max, useDetailed } = await req.json()

    if (!product) {
      return NextResponse.json(
        { error: "Product search term is required" },
        { status: 400 }
      )
    }

    // Build search conditions for products
    const searchTerms = product.toLowerCase().split(/\s+/).filter(Boolean)

    // Search products by name, description, SKU, or MPN
    const products = await prisma.product.findMany({
      where: {
        AND: [
          {
            OR: searchTerms.map((term: string) => ({
              OR: [
                { name: { contains: term, mode: 'insensitive' } },
                { description: { contains: term, mode: 'insensitive' } },
                { sku: { contains: term, mode: 'insensitive' } },
                { mpn: { contains: term, mode: 'insensitive' } },
              ]
            }))
          },
          { inStock: true }
        ]
      },
      include: {
        supplier: {
          select: {
            id: true,
            name: true,
            slug: true,
            contactEmail: true,
            contactPhone: true,
            website: true,
            description: true,
            industry: true,
            city: true,
            state: true,
            country: true,
          }
        }
      },
      take: 50, // Limit to 50 products
    })

    // Filter by location if provided
    let filteredProducts = products
    if (location) {
      const locationLower = location.toLowerCase()
      // Split location into parts to match flexibly (e.g., "Ithaca, New York" matches "Ithaca NY")
      const locationParts = locationLower.split(/[,\s]+/).filter(Boolean)

      filteredProducts = products.filter(p => {
        const supplierLocation = `${p.supplier.city} ${p.supplier.state} ${p.supplier.country}`.toLowerCase()
        // Check if any location part matches
        return locationParts.some((part: string) => supplierLocation.includes(part))
      })
    }

    // Group products by supplier and transform to Supplier format
    const supplierMap = new Map<string, any>()

    filteredProducts.forEach(product => {
      const supplierId = product.supplier.id

      if (!supplierMap.has(supplierId)) {
        // Extract price value for filtering
        let priceValue = 0
        if (product.priceText) {
          const numbers = product.priceText.match(/\d+\.?\d*/g)
          if (numbers && numbers.length > 0) {
            const prices = numbers.map(n => parseFloat(n))
            priceValue = prices.reduce((a, b) => a + b, 0) / prices.length
          }
        }

        // Skip if price is outside range (only if we have a valid price)
        if (priceValue > 0 && price_min !== undefined && price_max !== undefined) {
          if (priceValue < price_min || priceValue > price_max) {
            return
          }
        }

        supplierMap.set(supplierId, {
          name: product.supplier.name,
          location: `${product.supplier.city}, ${product.supplier.state}, ${product.supplier.country}`,
          product_title: product.name,
          units_sold: product.unit || "N/A",
          price_range: product.priceText || "Contact for pricing",
          website: product.supplier.website || "N/A",
          contact: product.supplier.contactEmail || product.supplier.contactPhone || "N/A",
          description: product.description || product.supplier.description || "",
          score: 85, // Default score for internal database suppliers
          source: "internal",
          supplierId: product.supplier.id,
          productCount: 1,
          products: [product],
        })
      } else {
        // Add product to existing supplier
        const supplier = supplierMap.get(supplierId)
        supplier.productCount++
        supplier.products.push(product)

        // Update product_title to show multiple products
        if (supplier.productCount === 2) {
          supplier.product_title = `${supplier.products[0].name} and 1 more product`
        } else if (supplier.productCount > 2) {
          supplier.product_title = `${supplier.products[0].name} and ${supplier.productCount - 1} more products`
        }
      }
    })

    let suppliers = Array.from(supplierMap.values())

    // If useDetailed is true, use Flask backend's sophisticated scoring
    if (useDetailed) {
      // Fetch detailed data for all suppliers and use Flask's ranking algorithm
      suppliers = await Promise.all(
        suppliers.map(async (supplier) => {
          try {
            // Fetch contracts and reviews in parallel from Flask backend
            const [contractsResponse, reviewsResponse] = await Promise.all([
              fetch(`${API_BASE_URL}/api/contracts/${encodeURIComponent(supplier.name)}`),
              fetch(`${API_BASE_URL}/api/reviews`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  company_name: supplier.name,
                  location: supplier.location,
                }),
              }),
            ])

            let contractsData = null
            let reviewsData = null

            if (contractsResponse.ok) {
              contractsData = await contractsResponse.json()
            }

            if (reviewsResponse.ok) {
              reviewsData = await reviewsResponse.json()
            }

            // Process contracts
            let contractsText = "None found"
            if (contractsData?.success && contractsData?.contracts) {
              contractsText = contractsData.contracts
            }

            // Process reviews
            let reviewsText = "No reviews found"
            if (reviewsData?.success && reviewsData?.reviews) {
              reviewsText = reviewsData.reviews
            }

            return {
              ...supplier,
              past_contracts: contractsText,
              reviews_mentions: reviewsText,
            }
          } catch (err) {
            console.error(`Error fetching details for ${supplier.name}:`, err)
            return supplier
          }
        })
      )

      // Use Flask backend's rank_suppliers endpoint to score all suppliers at once
      try {
        const rankResponse = await fetch(`${API_BASE_URL}/api/rank`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            suppliers,
            search_product: product,
            search_location: location || "",
            price_min: price_min || 0,
            price_max: price_max || 10000,
          }),
        })

        if (rankResponse.ok) {
          const rankedData = await rankResponse.json()
          // Add 7.5 bonus points for being in internal database
          suppliers = rankedData.suppliers.map((s: any) => ({
            ...s,
            score: Math.min((s.score || 0) + 12, 100), // Add internal bonus, cap at 100
          }))
        } else {
          // Fallback: if ranking fails, give default score with internal bonus
          suppliers = suppliers.map(s => ({
            ...s,
            score: 85,
          }))
        }
      } catch (err) {
        console.error("Error ranking suppliers:", err)
        // Fallback: give default score with internal bonus
        suppliers = suppliers.map(s => ({
          ...s,
          score: 85,
        }))
      }
    } else {
      // If not detailed, still add bonus points for being in internal database
      suppliers = suppliers.map(s => ({
        ...s,
        score: 85, // Base score + internal database bonus
      }))
    }

    return NextResponse.json({
      success: true,
      suppliers,
      count: suppliers.length,
    })
  } catch (error) {
    console.error("Internal search error:", error)
    return NextResponse.json(
      { error: "Failed to search internal database" },
      { status: 500 }
    )
  }
}
