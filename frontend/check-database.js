const { PrismaClient } = require('./src/generated/prisma')

const prisma = new PrismaClient()

async function main() {
  console.log('=== DATABASE CHECK ===\n')

  // Check Companies (Buyers)
  const companies = await prisma.company.findMany({
    select: {
      id: true,
      name: true,
      email: true,
      city: true,
      state: true,
      country: true,
    }
  })
  console.log(`📊 Companies (Buyers): ${companies.length}`)
  companies.forEach(c => console.log(`  - ${c.name} (${c.city}, ${c.state})`))
  console.log()

  // Check Suppliers
  const suppliers = await prisma.supplier.findMany({
    select: {
      id: true,
      name: true,
      contactEmail: true,
      city: true,
      state: true,
      country: true,
      industry: true,
      _count: {
        select: { products: true }
      }
    }
  })
  console.log(`🏭 Suppliers: ${suppliers.length}`)
  suppliers.forEach(s => console.log(`  - ${s.name} (${s.city}, ${s.state}) - ${s._count.products} products`))
  console.log()

  // Check Products
  const products = await prisma.product.findMany({
    select: {
      id: true,
      name: true,
      sku: true,
      priceText: true,
      unit: true,
      inStock: true,
      supplier: {
        select: {
          name: true
        }
      }
    }
  })
  console.log(`📦 Products: ${products.length}`)
  products.forEach(p => console.log(`  - ${p.name} (${p.priceText} ${p.unit}) - Supplier: ${p.supplier.name} - In Stock: ${p.inStock}`))
  console.log()

  // Check Users
  const users = await prisma.user.findMany({
    select: {
      id: true,
      email: true,
      role: true,
      companyId: true,
      supplierId: true,
    }
  })
  console.log(`👥 Users: ${users.length}`)
  users.forEach(u => console.log(`  - ${u.email} (${u.role})`))
  console.log()

  console.log('=== END ===')
}

main()
  .catch(e => {
    console.error('Error:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
