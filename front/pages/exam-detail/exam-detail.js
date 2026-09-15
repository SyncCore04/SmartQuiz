Page({
  data: {
    exam: {
      id: 1,
      title: '2024年高考语文模拟考试',
      cover: '/images/photo-1685287731216-a7a0fae7a41a_w400.jpg',
      date: '2024-03-15',
      time: '09:00 - 11:00',
      duration: '120分钟',
      totalCount: 50,
      totalScore: 150,
      joined: 1256,
      status: '进行中',
      rules: [
        '考试时间到后将自动提交试卷',
        '每人仅有一次考试机会',
        '考试过程中不可切换页面',
        '提交后可查看答案解析',
        '考试成绩将在考试结束后统一公布'
      ],
      sections: [
        { name: '选择题', count: 30, score: 60 },
        { name: '填空题', count: 10, score: 30 },
        { name: '阅读理解', count: 6, score: 36 },
        { name: '作文', count: 1, score: 24 }
      ]
    },
    historyScores: [
      { time: '第一次模考', score: 112, total: 150, rank: 156 },
      { time: '第二次模考', score: 125, total: 150, rank: 89 },
      { time: '第三次模考', score: 130, total: 150, rank: 45 }
    ]
  },
  onLoad() {},
  onStartExam() {
    wx.navigateTo({ url: '/pages/answer/answer' })
  }
})
