Page({
  data: {
    totalQuestions: 568,
    accuracy: '78%',
    streakDays: 15,
    weeklyData: [
      { day: '周一', value: 30, height: 60 },
      { day: '周二', value: 45, height: 90 },
      { day: '周三', value: 25, height: 50 },
      { day: '周四', value: 55, height: 110 },
      { day: '周五', value: 40, height: 80 },
      { day: '周六', value: 60, height: 120 },
      { day: '周日', value: 35, height: 70 }
    ],
    recentRecords: [
      { id: 1, title: '语文古诗词默写', score: 85, total: 100, date: '01-15', correct: 17, wrong: 3 },
      { id: 2, title: '数学函数专题', score: 72, total: 100, date: '01-14', correct: 18, wrong: 7 },
      { id: 3, title: '英语阅读理解', score: 90, total: 100, date: '01-13', correct: 9, wrong: 1 },
      { id: 4, title: '物理力学测试', score: 68, total: 100, date: '01-12', correct: 14, wrong: 6 }
    ]
  },
  onLoad() {}
})
