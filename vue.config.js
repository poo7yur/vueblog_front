const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  devServer: {
    port: 8080, // Vue默认端口（可省略，默认就是8080）
    open: false, // 启动后自动打开浏览器（可选）
    proxy: {
      // 匹配所有以 / 开头的请求（即所有接口请求）
      '/': {
        ws: false, //  关键：禁用该代理的 websocket
        target: 'http://172.16.161.40:8081', // 后台接口的基础地址
        changeOrigin: true, // 开启跨域（关键！代理服务器会伪造请求头的Origin）
        pathRewrite: {
          // 路径重写：因为target已经包含了基础地址，这里无需额外重写（若接口有前缀才需要）
          '^/': '/' 
        }
      }
    }
  }
})
