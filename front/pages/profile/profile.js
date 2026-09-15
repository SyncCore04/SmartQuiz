const { request, ensureUser } = require('../../utils/api')
const USER_KEY = 'smartquiz_user'

Page({
  data: {
    userInfo: { nickName: '加载中', avatar: '' },
    stats: [],
    showAbout: false,
    menuList: [
      { icon: 'records', name: '答题记录', desc: '查看历史答题情况', url: '/pages/stats/stats', bgColor: '#ede9fe', iconColor: '#4F46E5' },
      { icon: 'warning-o', name: '错题本', desc: '复习错题巩固知识', url: '/pages/wrong-book/wrong-book', bgColor: '#fee2e2', iconColor: '#EF4444' },
      { icon: 'chart-trending-o', name: '学习统计', desc: '数据分析学习趋势', url: '/pages/stats/stats', bgColor: '#d1fae5', iconColor: '#10B981' },
      { icon: 'info-o', name: '关于我们', desc: '了解更多产品信息', url: 'about', bgColor: '#fef3c7', iconColor: '#F59E0B' },
      { icon: 'revoke', name: '退出登录', desc: '', url: 'logout', bgColor: '#f3f4f6', iconColor: '#666' }
    ]
  },
  onLoad() {},
  onShow() {
    ensureUser().then(u => {
      return request('/api/profile?user_id=' + u.user_id)
    }).then(d => {
      this.setData({ userInfo: d.userInfo, stats: d.stats || [] })
    }).catch(() => {})
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 })
    }
  },
  onMenuTap(e) {
    const item = e.currentTarget.dataset.item
    if (item.url === 'about') {
      this.setData({ showAbout: true })
      return
    }
    if (item.url === 'logout') {
      this.onLogout()
      return
    }
    if (!item.url) return
    wx.navigateTo({ url: item.url })
  },
  onCloseAbout() {
    this.setData({ showAbout: false })
  },
  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      showCancel: true,
      success: res => {
        if (res.confirm) {
          wx.removeStorageSync(USER_KEY)
          wx.showToast({ title: '已退出', icon: 'none' })
          this.setData({ userInfo: { nickName: '未登录', avatar: '' }, stats: [] })
        }
      }
    })
  }
})