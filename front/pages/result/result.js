Page({
  data: {
    score: 85,
    totalQuestions: 10,
    correctCount: 8,
    wrongCount: 2,
    accuracy: '80%',
    timeUsed: '12分30秒',
    results: [
      { id: 1, num: 1, isCorrect: true, myAnswer: 'B', correctAnswer: 'B', title: '下列词语中，没有错别字的一组是？' },
      { id: 2, num: 2, isCorrect: true, myAnswer: 'B', correctAnswer: 'B', title: '已知函数 f(x) = x³ - 3x + 1，则极小值为？' },
      { id: 3, num: 3, isCorrect: true, myAnswer: 'A', correctAnswer: 'A', title: 'The teacher asked us to ______ the homework.' },
      { id: 4, num: 4, isCorrect: false, myAnswer: 'A', correctAnswer: 'B', title: '下列文学作品与其作者对应正确的是？' },
      { id: 5, num: 5, isCorrect: true, myAnswer: 'B', correctAnswer: 'B', title: '地球是太阳系中最大的行星。' },
      { id: 6, num: 6, isCorrect: true, myAnswer: 'B', correctAnswer: 'B', title: '水在标准大气压下的沸点是多少？' },
      { id: 7, num: 7, isCorrect: true, myAnswer: 'C', correctAnswer: 'C', title: '光合作用主要发生在植物的哪个部位？' },
      { id: 8, num: 8, isCorrect: true, myAnswer: 'C', correctAnswer: 'C', title: '化学反应2H₂+O₂→2H₂O中，生成物是什么？' },
      { id: 9, num: 9, isCorrect: false, myAnswer: 'A', correctAnswer: 'B', title: '唐朝的开国皇帝是谁？' },
      { id: 10, num: 10, isCorrect: true, myAnswer: 'B', correctAnswer: 'B', title: '赤道周长约为多少公里？' }
    ]
  },
  onLoad() {},
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
