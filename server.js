const express = require('express');
const cors = require('cors');
const https = require('https');

const app = express();
const PORT = process.env.PORT || 8080;

// 从环境变量读取配置
const SHOPIFY_STORE = process.env.SHOPIFY_STORE || 'goldianlightandliving.myshopify.com';
const SHOPIFY_TOKEN = process.env.SHOPIFY_TOKEN || '';

// 启用 CORS
app.use(cors());
app.use(express.json());

// 健康检查
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    shopifyStore: SHOPIFY_STORE
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
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: JSON.parse(data)
          });
        } catch (error) {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: data // Return raw data if JSON parsing fails
          });
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

// 获取产品分类信息
async function getProductCategories() {
  try {
    const options = {
      hostname: SHOPIFY_STORE,
      port: 443,
      path: '/admin/api/2023-10/custom_collections.json',
      method: 'GET',
      headers: {
        'X-Shopify-Access-Token': SHOPIFY_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    const response = await makeHttpsRequest(options);
    
    if (response.statusCode === 200 && response.data.custom_collections) {
      return response.data.custom_collections;
    } else {
      console.log('[API] No custom collections found or error occurred');
      return [];
    }
  } catch (error) {
    console.error('[API] Error fetching collections:', error);
    return [];
  }
}

// 获取智能集合
async function getSmartCollections() {
  try {
    const options = {
      hostname: SHOPIFY_STORE,
      port: 443,
      path: '/admin/api/2023-10/smart_collections.json',
      method: 'GET',
      headers: {
        'X-Shopify-Access-Token': SHOPIFY_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    const response = await makeHttpsRequest(options);
    
    if (response.statusCode === 200 && response.data.smart_collections) {
      return response.data.smart_collections;
    } else {
      console.log('[API] No smart collections found or error occurred');
      return [];
    }
  } catch (error) {
    console.error('[API] Error fetching smart collections:', error);
    return [];
  }
}

// 获取所有产品及其分类信息（分页处理）
app.get('/api/shopify/products', async (req, res) => {
  try {
    console.log('[API] Fetching ALL products and collections from Shopify...');
    
    let allProducts = [];
    let nextPageUrl = `/admin/api/2023-10/products.json`;
    
    // 获取所有产品（分页）
    while (nextPageUrl) {
      const productsOptions = {
        hostname: SHOPIFY_STORE,
        port: 443,
        path: nextPageUrl.startsWith('http') ? new URL(nextPageUrl).pathname + new URL(nextPageUrl).search : nextPageUrl,
        method: 'GET',
        headers: {
          'X-Shopify-Access-Token': SHOPIFY_TOKEN,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      };
      
      const productsResponse = await makeHttpsRequest(productsOptions);
      
      console.log('[API] Shopify products response status:', productsResponse.statusCode);
      
      if (productsResponse.statusCode !== 200) {
        throw new Error(`Shopify API error: ${productsResponse.statusCode} - ${JSON.stringify(productsResponse.data)}`);
      }
      
      if (!productsResponse.data || !productsResponse.data.products) {
        throw new Error('Invalid response format from Shopify API');
      }
      
      console.log('[API] Fetched batch:', productsResponse.data.products.length, 'products');
      
      allProducts = allProducts.concat(productsResponse.data.products);
      
      // 检查是否有下一页
      if (productsResponse.headers.link) {
        const links = productsResponse.headers.link.split(',');
        const nextLink = links.find(link => link.includes('rel="next"'));
        if (nextLink) {
          const match = nextLink.match(/<([^>]+)>/);
          if (match) {
            nextPageUrl = match[1];
            // 提取路径部分
            nextPageUrl = new URL(nextPageUrl).pathname + new URL(nextPageUrl).search;
          } else {
            nextPageUrl = null;
          }
        } else {
          nextPageUrl = null;
        }
      } else {
        nextPageUrl = null;
      }
    }
    
    console.log('[API] Total products fetched:', allProducts.length);
    
    // 获取分类信息
    const customCollections = await getProductCategories();
    const smartCollections = await getSmartCollections();
    
    // 合并所有集合
    const allCollections = [...customCollections, ...smartCollections];
    
    // 创建产品ID到集合的映射
    const productCollectionMap = {};
    allCollections.forEach(collection => {
      if (collection.products) {
        collection.products.forEach(product => {
          if (!productCollectionMap[product.id]) {
            productCollectionMap[product.id] = [];
          }
          productCollectionMap[product.id].push({
            id: collection.id,
            title: collection.title,
            handle: collection.handle
          });
        });
      }
    });
    
    // 处理产品数据，添加分类和电商平台链接
    const processedProducts = allProducts.map((product) => {
      const productTitle = product.title || '';
      
      // 获取产品的分类
      const collections = productCollectionMap[product.id] || [];
      
      // 尝试从产品类型推断分类
      let category = 'General';
      if (product.product_type && product.product_type.trim() !== '') {
        category = product.product_type;
      } else if (collections.length > 0) {
        category = collections[0].title;
      } else {
        // 从标题中推断类别
        const title = product.title.toLowerCase();
        if (title.includes('lamp') || title.includes('light') || title.includes('chandelier') || title.includes('sconce')) {
          category = 'Lighting';
        } else if (title.includes('table') || title.includes('desk')) {
          category = 'Furniture';
        } else if (title.includes('outdoor') || title.includes('wall')) {
          category = 'Outdoor';
        } else if (title.includes('floor')) {
          category = 'Floor Lamps';
        } else if (title.includes('pendant')) {
          category = 'Pendants';
        } else if (title.includes('ceiling')) {
          category = 'Ceiling Lights';
        } else if (title.includes('bedroom') || title.includes('nightstand')) {
          category = 'Bedroom';
        } else if (title.includes('bathroom')) {
          category = 'Bathroom';
        } else if (title.includes('kitchen')) {
          category = 'Kitchen';
        } else {
          category = 'Home Decor';
        }
      }
      
      return {
        id: product.id,
        title: product.title,
        description: product.body_html || product.body_text || '',
        images: product.images || [],
        variants: product.variants || [],
        category: category, // Add category to product
        collections: collections, // Add collection information
        platformLinks: {
          wayfair: '',
          amazon: '',
          overstock: '',
          homeDepot: '',
          lowes: '',
          target: '',
          kohls: ''
        }
      };
    });
    
    console.log(`[API] Processed ${processedProducts.length} products successfully`);
    console.log(`[API] Found ${allCollections.length} collections`);
    
    res.json(processedProducts);
    
  } catch (error) {
    console.error('[API] Error:', error);
    res.status(500).json({ 
      error: 'Failed to fetch products', 
      details: error.message 
    });
  }
});

// 获取所有分类
app.get('/api/shopify/categories', async (req, res) => {
  try {
    console.log('[API] Fetching categories...');
    
    // 获取产品
    const productsOptions = {
      hostname: SHOPIFY_STORE,
      port: 443,
      path: '/admin/api/2023-10/products.json',
      method: 'GET',
      headers: {
        'X-Shopify-Access-Token': SHOPIFY_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    const productsResponse = await makeHttpsRequest(productsOptions);
    
    if (productsResponse.statusCode !== 200) {
      throw new Error(`Shopify API error: ${productsResponse.statusCode}`);
    }
    
    if (!productsResponse.data || !productsResponse.data.products) {
      throw new Error('Invalid response format from Shopify API');
    }
    
    // 获取所有唯一的产品类型
    const uniqueTypes = [...new Set(productsResponse.data.products.map(p => p.product_type))];
    const filteredTypes = uniqueTypes.filter(type => type && type.trim() !== '');
    
    // 从标题推断的类别
    const inferredCategories = ['Lighting', 'Furniture', 'Outdoor', 'Floor Lamps', 'Pendants', 'Home Decor'];
    
    const allCategories = [...new Set([...filteredTypes, ...inferredCategories])].sort();
    
    res.json(allCategories);
    
  } catch (error) {
    console.error('[API] Error fetching categories:', error);
    res.status(500).json({ 
      error: 'Failed to fetch categories', 
      details: error.message 
    });
  }
});

// 内存存储平台链接数据（生产环境建议使用数据库）
const platformLinksStore = new Map();

// 获取所有平台链接
app.get('/api/platform-links', (req, res) => {
  console.log('[API] Fetching all platform links');
  const links = {};
  platformLinksStore.forEach((value, key) => {
    links[key] = value;
  });
  res.json(links);
});

// 获取单个产品的平台链接
app.get('/api/platform-links/:productId', (req, res) => {
  const { productId } = req.params;
  console.log(`[API] Fetching platform links for product: ${productId}`);
  const links = platformLinksStore.get(productId) || {
    wayfair: '',
    amazon: '',
    overstock: '',
    homeDepot: '',
    lowes: '',
    target: '',
    kohls: ''
  };
  res.json(links);
});

// 更新单个产品的平台链接
app.post('/api/platform-links/:productId', (req, res) => {
  const { productId } = req.params;
  const links = req.body;
  
  console.log(`[API] Updating platform links for product: ${productId}`, links);
  
  // 验证链接数据
  const validPlatforms = ['wayfair', 'amazon', 'overstock', 'homeDepot', 'lowes', 'target', 'kohls'];
  const sanitizedLinks = {};
  
  validPlatforms.forEach(platform => {
    sanitizedLinks[platform] = links[platform] || '';
  });
  
  platformLinksStore.set(productId, sanitizedLinks);
  
  res.json({ 
    success: true, 
    message: 'Platform links updated successfully',
    productId,
    links: sanitizedLinks
  });
});

// 批量更新平台链接
app.post('/api/platform-links/bulk', (req, res) => {
  const { links } = req.body;
  
  console.log('[API] Bulk updating platform links');
  
  if (!links || typeof links !== 'object') {
    return res.status(400).json({ 
      success: false, 
      error: 'Invalid data format' 
    });
  }
  
  let updatedCount = 0;
  Object.keys(links).forEach(productId => {
    const productLinks = links[productId];
    if (productLinks && typeof productLinks === 'object') {
      platformLinksStore.set(productId, productLinks);
      updatedCount++;
    }
  });
  
  res.json({ 
    success: true, 
    message: `Updated ${updatedCount} products`,
    updatedCount
  });
});

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
  console.log('====================================');
  console.log('✅ Server ready to proxy requests');
  console.log('====================================');
});
