// API client for Flask backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"

export interface Supplier {
  name: string
  location: string
  product_title: string
  units_sold: string
  price_range: string
  website?: string
  contact?: string
  description: string
  past_contracts?: string
  reviews_mentions?: string
  score?: number
  source?: "internal" | "gpt"
  supplierId?: string
}

interface SearchParams {
  product: string
  location: string
  price_min: number
  price_max: number
}

interface SearchResponse {
  success: boolean
  suppliers: Supplier[]
  error?: string
}

export async function searchSuppliers(params: SearchParams): Promise<SearchResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return {
      success: true,
      suppliers: data.suppliers || [],
    }
  } catch (error) {
    console.error("Search error:", error)
    return {
      success: false,
      suppliers: [],
      error: error instanceof Error ? error.message : "Failed to search suppliers",
    }
  }
}

export async function searchSuppliersDetailed(params: SearchParams): Promise<SearchResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/search/detailed`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return {
      success: true,
      suppliers: data.suppliers || [],
    }
  } catch (error) {
    console.error("Detailed search error:", error)
    return {
      success: false,
      suppliers: [],
      error: error instanceof Error ? error.message : "Failed to search suppliers",
    }
  }
}

export async function searchSuppliersCombined(params: SearchParams & { useDetailed?: boolean }): Promise<SearchResponse> {
  try {
    const response = await fetch("/api/search/combined", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return {
      success: true,
      suppliers: data.suppliers || [],
    }
  } catch (error) {
    console.error("Combined search error:", error)
    return {
      success: false,
      suppliers: [],
      error: error instanceof Error ? error.message : "Failed to search suppliers",
    }
  }
}
