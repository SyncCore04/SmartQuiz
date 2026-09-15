const { request } = require('../../utils/api')

Page({
  data: {
    exams: []
  },
  onLoad() {
    request('/api/exams').then(list => {
      this.setData({ exams: list || [] })
    }).catch(() => {})
  },
  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
  },
  onExamTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/exam-detail/exam-detail?examId=' + id })
  }
})