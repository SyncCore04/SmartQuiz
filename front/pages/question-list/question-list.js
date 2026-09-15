const { request } = require('../../utils/api')

Page({
  data: {
    activeFilter: 'all',
    filters: [
      { key: 'all', label: '全部' },
      { key: 'single', label: '单选题' },
      { key: 'multi', label: '多选题' },
      { key: 'judge', label: '判断题' },
      { key: 'fill', label: '填空题' }
    ],
    questions: [],
    allQuestions: []
  },
  onLoad(options) {
    const qs = []
    if (options && options.categoryId) qs.push('category_id=' + options.categoryId)
    if (options && options.bankId) qs.push('bank_id=' + options.bankId)
    const url = '/api/questions' + (qs.length ? '?' + qs.join('&') : '')
    request(url).then(list => {
      this.setData({ allQuestions: list || [], questions: list || [] })
    }).catch(() => {})
  },
  onFilterTap(e) {
    const key = e.currentTarget.dataset.key
    const filtered = key === 'all'
      ? this.data.allQuestions
      : this.data.allQuestions.filter(x => x.typeKey === key)
    this.setData({ activeFilter: key, questions: filtered })
  },
  onQuestionTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/answer/answer?questionId=' + id })
  }
})