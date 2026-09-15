const { request, ensureUser } = require('../../utils/api')
const PRACTICE_STYLE = { icon: 'records', bgColor: '#ede9fe', iconColor: '#4F46E5' }

Page({
  data: {
    swiperList: [],
    categories: [],
    hotBanks: [],
    recentPractices: [],
    notice: '系统将于本周六进行维护升级，届时部分功能暂不可用，敬请谅解。',
    overview: { done: 0, accuracy: '0%', streak: 0 }
  },
  onLoad() {
    ensureUser().then(u => {
      return Promise.all([
        request('/api/swipers'),
        request('/api/categories'),
        request('/api/banks'),
        request('/api/stats/overview?user_id=' + u.user_id),
        request('/api/records?user_id=' + u.user_id)
      ])
    }).then(([sw, cat, bk, st, rc]) => {
      this.setData({
        swiperList: sw || [],
        categories: cat || [],
        hotBanks: (bk || []).map(b => ({
          id: b.id, title: b.title, desc: b.desc, image: b.cover,
          count: b.count, joined: b.joined, tag: b.tag
        })),
        recentPractices: (rc || []).map(r => Object.assign({}, PRACTICE_STYLE, {
          id: r.id, title: r.title, score: r.score, total: r.total, date: r.date
        })),
        overview: { done: st.totalQuestions, accuracy: st.accuracy, streak: st.streakDays }
      })
    }).catch(() => {})
  },
  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
  },
  onSearch() {
    wx.navigateTo({ url: '/pages/category/category' })
  },
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question-list/question-list?categoryId=' + id })
  },
  onHotBankTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question-list/question-list?bankId=' + id })
  },
  onPracticeTap() {
    wx.navigateTo({ url: '/pages/answer/answer' })
  }
})