Page({
  data: {
    score: 0,
    totalQuestions: 0,
    correctCount: 0,
    wrongCount: 0,
    accuracy: '0%',
    timeUsed: '--',
    results: []
  },
  onLoad() {
    const d = wx.getStorageSync('last_submit') || {}
    this.setData({
      score: d.score || 0,
      totalQuestions: d.total || 0,
      correctCount: d.correct || 0,
      wrongCount: d.wrong || 0,
      accuracy: d.accuracy || '0%',
      timeUsed: d.timeUsed || '--',
      results: d.results || []
    })
  },
  onRetry() {
    wx.navigateTo({ url: '/pages/answer/answer' })
  },
  onViewWrong() {
    wx.navigateTo({ url: '/pages/wrong-book/wrong-book' })
  },
  onBackHome() {
    wx.switchTab({ url: '/pages/index/index' })
  }
})