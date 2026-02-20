const express = require('express');
const cors = require('cors');
const https = require('https');
const mongoose = require('mongoose');

const app = express();
const PORT = process.env.PORT || 8080;

// 从环境变量读取配置
const SHOPIFY_STORE = process.env.SHOPIFY_STORE || 'goldianlightandliving.myshopify.com';
const SHOPIFY_TOKEN = process.env.SHOPIFY_TOKEN || '';
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/aloadecor';

// 启用 CORS
app.use(cors());
app.use(express.json());

// 连接 MongoDB
console.log('[Database] Attempting to connect to MongoDB...');
console.log('[Database] Connection string (masked):', MONGODB_URI.replace(/:([^@]+)@/, ':****@'));

mongoose.connect(MONGODB_URI)
  .then(() => {
    console.log('[Database] ✅ Connected to MongoDB successfully');
  })
  .catch(err => {
    console.error('[Database] ❌ MongoDB connection error:', err.message);
    console.error('[Database] Error code:', err.code);
    console.error('[Database] Error name:', err.name);
  });

// 监听连接事件
mongoose.connection.on('connected', () => {
  console.log('[Database] Mongoose connected to MongoDB');
});

mongoose.connection.on('error', (err) => {
  console.error('[Database] Mongoose connection error:', err.message);
});

mongoose.connection.on('disconnected', () => {
  console.log('[Database] Mongoose disconnected from MongoDB');
});

// 定义平台链接 Schema
const platformLinkSchema = new mongoose.Schema({
  productId: { type: String, required: true, unique: true },
  amazon1: { type: String, default: '' },
  amazon2: { type: String, default: '' },
  wf1: { type: String, default: '' },
  wf2: { type: String, default: '' },
  os1: { type: String, default: '' },
  os2: { type: String, default: '' },
  hd1: { type: String, default: '' },
  hd2: { type: String, default: '' },
  lowes: { type: String, default: '' },
  target: { type: String, default: '' },
  walmart: { type: String, default: '' },
  ebay: { type: String, default: '' },
  kohls: { type: String, default: '' },
  updatedAt: { type: Date, default: Date.now }
});

const PlatformLink = mongoose.model('PlatformLink', platformLinkSchema);

// 健康检查
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    shopifyStore: SHOPIFY_STORE,
    database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected'
  });
});

// 发起 HTTPS 请求的辅助函数
function makeHttpsRequest(options, postData = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsedData = JSON.parse(data);
          resolve({ statusCode: res.statusCode, data: parsedData });
        } catch (e) {
          resolve({ statusCode: res.statusCode, data: data });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    if (postData) {
      req.write(postData);
    }
    
    req.end();
  });
}

// 获取所有产品
app.get('/api/shopify/products', async (req, res) => {
  console.log('[API] Fetching all products from Shopify...');
  
  try {
    // 检查 token 是否配置
    if (!SHOPIFY_TOKEN) {
      console.log('[API] No Shopify token configured, returning mock data');
      const mockProducts = getMockProducts();
      return res.json(mockProducts);
    }
    
    // 从 Shopify 获取产品（带分页）
    let allProducts = [];
    let hasNextPage = true;
    let nextPageInfo = null;
    const limit = 250; // Shopify 最大每页数量
    let pageCount = 0;
    const maxPages = 10; // 最多获取 2500 个产品
    
    while (hasNextPage && pageCount < maxPages) {
      pageCount++;
      console.log(`[API] Fetching page ${pageCount}...`);
      
      // 构建请求 URL
      let urlPath = `/admin/api/2024-01/products.json?limit=${limit}`;
      if (nextPageInfo) {
        urlPath += `&page_info=${nextPageInfo}`;
      }
      
      const options = {
        hostname: SHOPIFY_STORE,
        path: urlPath,
        method: 'GET',
        headers: {
          'X-Shopify-Access-Token': SHOPIFY_TOKEN,
          'Content-Type': 'application/json'
        }
      };
      
      const response = await makeHttpsRequest(options);
      
      if (response.statusCode !== 200) {
        console.error('[API] Shopify API error:', response.data);
        throw new Error(`Shopify API returned ${response.statusCode}`);
      }
      
      const products = response.data.products || [];
      allProducts = allProducts.concat(products);
      
      console.log(`[API] Fetched ${products.length} products (total: ${allProducts.length})`);
      
      // 检查是否有下一页
      // Shopify 在 Link header 中返回分页信息
      hasNextPage = false; // 简化处理，如果需要分页可以重新实现
      
      if (products.length < limit) {
        hasNextPage = false;
      }
    }
    
    console.log(`[API] Total products fetched: ${allProducts.length}`);
    
    // 获取所有平台链接数据
    const platformLinksData = await PlatformLink.find({});
    const linksMap = {};
    platformLinksData.forEach(link => {
      linksMap[link.productId] = {
        amazon1: link.amazon1 || '',
        amazon2: link.amazon2 || '',
        wf1: link.wf1 || '',
        wf2: link.wf2 || '',
        os1: link.os1 || '',
        os2: link.os2 || '',
        hd1: link.hd1 || '',
        hd2: link.hd2 || '',
        lowes: link.lowes || '',
        target: link.target || '',
        walmart: link.walmart || '',
        ebay: link.ebay || '',
        kohls: link.kohls || ''
      };
    });
    
    // 格式化产品数据
    const formattedProducts = allProducts.map(product => ({
      id: String(product.id),
      title: product.title,
      description: product.body_html || '',
      images: product.images || [],
      variants: product.variants || [],
      category: product.product_type || 'Uncategorized',
      collections: [],
      platformLinks: linksMap[String(product.id)] || {
        amazon1: '',
        amazon2: '',
        wf1: '',
        wf2: '',
        os1: '',
        os2: '',
        hd1: '',
        hd2: '',
        lowes: '',
        target: '',
        walmart: '',
        ebay: '',
        kohls: ''
      }
    }));
    
    res.json(formattedProducts);
    
  } catch (error) {
    console.error('[API] Error fetching products:', error);
    // 返回 mock 数据作为后备
    const mockProducts = getMockProducts();
    res.json(mockProducts);
  }
});

// 获取分类列表
app.get('/api/shopify/categories', async (req, res) => {
  console.log('[API] Fetching categories...');
  
  try {
    if (!SHOPIFY_TOKEN) {
      console.log('[API] No token, returning mock categories');
      return res.json(['Lighting', 'Furniture', 'Decor', 'Outdoor']);
    }
    
    const options = {
      hostname: SHOPIFY_STORE,
      path: '/admin/api/2024-01/products.json?fields=product_type&limit=250',
      method: 'GET',
      headers: {
        'X-Shopify-Access-Token': SHOPIFY_TOKEN,
        'Content-Type': 'application/json'
      }
    };
    
    const response = await makeHttpsRequest(options);
    
    if (response.statusCode !== 200) {
      throw new Error(`Shopify API returned ${response.statusCode}`);
    }
    
    const products = response.data.products || [];
    const categories = [...new Set(products.map(p => p.product_type).filter(Boolean))];
    
    res.json(categories);
    
  } catch (error) {
    console.error('[API] Error fetching categories:', error);
    res.status(500).json({ 
      error: 'Failed to fetch categories', 
      details: error.message 
    });
  }
});

// 获取所有平台链接
app.get('/api/platform-links', async (req, res) => {
  console.log('[API] Fetching all platform links from MongoDB');
  try {
    const links = await PlatformLink.find({});
    const linksMap = {};
    links.forEach(link => {
      linksMap[link.productId] = {
        amazon1: link.amazon1 || '',
        amazon2: link.amazon2 || '',
        wf1: link.wf1 || '',
        wf2: link.wf2 || '',
        os1: link.os1 || '',
        os2: link.os2 || '',
        hd1: link.hd1 || '',
        hd2: link.hd2 || '',
        lowes: link.lowes || '',
        target: link.target || '',
        walmart: link.walmart || '',
        ebay: link.ebay || '',
        kohls: link.kohls || ''
      };
    });
    res.json(linksMap);
  } catch (error) {
    console.error('[API] Error fetching platform links:', error);
    res.status(500).json({ error: 'Failed to fetch platform links' });
  }
});

// 获取单个产品的平台链接
app.get('/api/platform-links/:productId', async (req, res) => {
  const { productId } = req.params;
  console.log(`[API] Fetching platform links for product: ${productId}`);
  try {
    const link = await PlatformLink.findOne({ productId });
    if (link) {
      res.json({
        amazon1: link.amazon1 || '',
        amazon2: link.amazon2 || '',
        wf1: link.wf1 || '',
        wf2: link.wf2 || '',
        os1: link.os1 || '',
        os2: link.os2 || '',
        hd1: link.hd1 || '',
        hd2: link.hd2 || '',
        lowes: link.lowes || '',
        target: link.target || '',
        walmart: link.walmart || '',
        ebay: link.ebay || '',
        kohls: link.kohls || ''
      });
    } else {
      res.json({
        amazon1: '',
        amazon2: '',
        wf1: '',
        wf2: '',
        os1: '',
        os2: '',
        hd1: '',
        hd2: '',
        lowes: '',
        target: '',
        walmart: '',
        ebay: '',
        kohls: ''
      });
    }
  } catch (error) {
    console.error('[API] Error fetching platform links:', error);
    res.status(500).json({ error: 'Failed to fetch platform links' });
  }
});

// 更新单个产品的平台链接
app.post('/api/platform-links/:productId', async (req, res) => {
  const { productId } = req.params;
  const links = req.body;
  
  console.log(`[API] Updating platform links for product: ${productId}`, links);
  
  // 验证链接数据
  const validPlatforms = ['amazon1', 'amazon2', 'wf1', 'wf2', 'os1', 'os2', 'hd1', 'hd2', 'lowes', 'target', 'walmart', 'ebay', 'kohls'];
  const sanitizedLinks = {};
  
  validPlatforms.forEach(platform => {
    sanitizedLinks[platform] = links[platform] || '';
  });
  
  try {
    // 使用 upsert 更新或创建
    const result = await PlatformLink.findOneAndUpdate(
      { productId },
      { 
        ...sanitizedLinks,
        updatedAt: new Date()
      },
      { upsert: true, new: true }
    );
    
    console.log(`[API] Platform links saved for product: ${productId}`);
    
    res.json({ 
      success: true, 
      message: 'Platform links updated successfully',
      productId,
      links: sanitizedLinks
    });
  } catch (error) {
    console.error('[API] Error saving platform links:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to save platform links'
    });
  }
});

// 批量更新平台链接
app.post('/api/platform-links/bulk', async (req, res) => {
  const { links } = req.body;
  
  console.log('[API] Bulk updating platform links');
  
  if (!links || typeof links !== 'object') {
    return res.status(400).json({ 
      success: false, 
      error: 'Invalid data format' 
    });
  }
  
  try {
    let updatedCount = 0;
    const validPlatforms = ['amazon1', 'amazon2', 'wf1', 'wf2', 'os1', 'os2', 'hd1', 'hd2', 'lowes', 'target', 'walmart', 'ebay', 'kohls'];

    for (const productId of Object.keys(links)) {
      const productLinks = links[productId];
      if (productLinks && typeof productLinks === 'object') {
        const sanitizedLinks = {};
        validPlatforms.forEach(platform => {
          sanitizedLinks[platform] = productLinks[platform] || '';
        });
        
        await PlatformLink.findOneAndUpdate(
          { productId },
          { 
            ...sanitizedLinks,
            updatedAt: new Date()
          },
          { upsert: true }
        );
        updatedCount++;
      }
    }
    
    console.log(`[API] Bulk update completed: ${updatedCount} products`);
    
    res.json({ 
      success: true, 
      message: `Updated ${updatedCount} products`,
      updatedCount
    });
  } catch (error) {
    console.error('[API] Error in bulk update:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to save platform links'
    });
  }
});

// Mock 数据函数
function getMockProducts() {
  return [
    {
      id: "1",
      title: "Modern Crystal Chandelier",
      description: "Elegant crystal chandelier perfect for dining rooms",
      images: [{ src: "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=400" }],
      variants: [{ title: "Default", price: "299.99", sku: "CH-001" }],
      category: "Lighting",
      collections: [],
      platformLinks: {
        wayfair: "",
        amazon: "",
        overstock: "",
        homeDepot: "",
        lowes: "",
        target: "",
        kohls: ""
      }
    },
    {
      id: "2",
      title: "Vintage Table Lamp",
      description: "Classic vintage style table lamp",
      images: [{ src: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400" }],
      variants: [{ title: "Default", price: "89.99", sku: "TL-002" }],
      category: "Lighting",
      collections: [],
      platformLinks: {
        wayfair: "",
        amazon: "",
        overstock: "",
        homeDepot: "",
        lowes: "",
        target: "",
        kohls: ""
      }
    },
    {
      id: "3",
      title: "LED Floor Lamp",
      description: "Modern LED floor lamp with adjustable brightness",
      images: [{ src: "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400" }],
      variants: [{ title: "Default", price: "149.99", sku: "FL-003" }],
      category: "Lighting",
      collections: [],
      platformLinks: {
        wayfair: "",
        amazon: "",
        overstock: "",
        homeDepot: "",
        lowes: "",
        target: "",
        kohls: ""
      }
    }
  ];
}

// 启动服务器
app.listen(PORT, () => {
  console.log('====================================');
  console.log('=== Shopify API Proxy Server ===');
  console.log('====================================');
  console.log(`Server running on: http://localhost:${PORT}`);
  console.log(`Health check:     http://localhost:${PORT}/health`);
  console.log(`Products API:     http://localhost:${PORT}/api/shopify/products`);
  console.log(`Categories API:   http://localhost:${PORT}/api/shopify/categories`);
  console.log(`Platform Links:   http://localhost:${PORT}/api/platform-links`);
  console.log(`Shopify store:    ${SHOPIFY_STORE}`);
  console.log(`Database:         ${MONGODB_URI.includes('localhost') ? 'Local MongoDB' : 'MongoDB Atlas'}`);
  console.log('====================================');
  console.log('✅ Server ready to proxy requests');
  console.log('====================================');
});
