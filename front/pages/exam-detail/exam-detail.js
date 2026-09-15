const { request } = require('../../utils/api')

const DEFAULT_RULES = [
  '考试时间到后将自动提交试卷',
  '每人仅有一次考试机会',
  '考试过程中不可切换页面',
  '提交后可查看答案解析',
  '考试成绩将在考试结束后统一公布'
]

Page({
  data: {
    exam: {
      id: 0, cover: '', title: '', time: '--', duration: '--',
      totalCount: 0, totalScore: '--', joined: 0, status: '',
      sections: [], rules: DEFAULT_RULES
    },
    historyScores: [
      { time: '第一次模考', score: 112, total: 150, rank: 156 },
      { time: '第二次模考', score: 125, total: 150, rank: 89 },
      { time: '第三次模考', score: 130, total: 150, rank: 45 }
    ]
  },
  onLoad(options) {
    if (!options || !options.examId) return
    request('/api/exams/' + options.examId).then(d => {
      this.setData({
        exam: {
          id: d.id, cover: d.cover, title: d.title, time: d.date, duration: d.duration,
          totalCount: d.totalCount, totalScore: '--', joined: d.joined, status: d.status,
          sections: [{ name: '全部题目', count: d.totalCount, score: '--' }],
          rules: DEFAULT_RULES
        }
      })
    }).catch(() => {})
  },
  onStartExam() {
    wx.navigateTo({ url: '/pages/answer/answer' })
  }
})