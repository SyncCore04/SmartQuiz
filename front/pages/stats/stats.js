const { request, ensureUser } = require('../../utils/api')

Page({
  data: {
    totalQuestions: 0,
    accuracy: '0%',
    streakDays: 0,
    weeklyData: [],
    recentRecords: []
  },
  onShow() {
    ensureUser().then(u => {
      return Promise.all([
        request('/api/stats/overview?user_id=' + u.user_id),
        request('/api/records?user_id=' + u.user_id)
      ])
    }).then(([st, rc]) => {
      this.setData({
        totalQuestions: st.totalQuestions,
        accuracy: st.accuracy,
        streakDays: st.streakDays,
        weeklyData: st.weeklyData || [],
        recentRecords: rc || []
      })
    }).catch(() => {})
  }
})