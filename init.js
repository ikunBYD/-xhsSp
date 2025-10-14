// 该文件在浏览器加载之初用于修改指纹减少被杀风险
(() => {
  try {
    // （1) 覆盖 navigator.webdriver → 返回 undefined（模拟真实浏览器）
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
      configurable: true
      }
    // （1) 设置浏览器的默认语言类型
    Object.defineProperty(navigator,'languages',{
      get: ()=> ['zh-CN', 'zh'],
      configurable:true
    })
    }
    });