const { ensureUser } = require('./utils/api')
App({
  onLaunch() {
    // 启动时静默登录，拿到游客 user_id
    ensureUser().catch(() => {})
  },
  globalData: {
    userInfo: null,
    themeColor: '#4F46E5',
    themeColorLight: '#ede9fe',
    accentColor: '#7C3AED'
  }
})