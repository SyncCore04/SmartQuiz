const { request, ensureUser } = require('../../utils/api')
// 仅支持有选项的题型（单选/多选/判断）
const ANSWER_TYPES = ['single', 'multi', 'judge']

// 把后端返回的选项文本 "A. xxx B. xxx" 解析成 [{key,text,selected}]
function parseOptions(text) {
  if (!text) return []
  const arr = []
  const re = /([A-Z])[\.、]?\s*(.*?)(?=\s+[A-Z][\.、]|$)/g
  let m
  while ((m = re.exec(text)) !== null) {
    arr.push({ key: m[1], text: m[2], selected: false })
  }
  return arr
}

Page({
  data: {
    currentIndex: 0,
    questions: []
  },
  onLoad(options) {
    request('/api/questions').then(list => {
      let qs = (list || []).filter(q => ANSWER_TYPES.indexOf(q.typeKey) > -1)
        .map(q => ({ id: q.id, type: q.type, title: q.title, options: parseOptions(q.options) }))
      // 指定了题目时只展示该题
      if (options && options.questionId) {
        const found = qs.find(q => String(q.id) === String(options.questionId))
        if (found) qs = [found]
      }
      this.setData({ questions: qs })
    }).catch(() => {})
  },
  onOptionTap(e) {
    const qIdx = e.currentTarget.dataset.qindex
    const oIdx = e.currentTarget.dataset.oindex
    const q = this.data.questions[qIdx]
    const isMulti = q.type.indexOf('多选') > -1
    const options = q.options.map((opt, i) => {
      if (!isMulti) return { key: opt.key, text: opt.text, selected: i === oIdx }
      // 多选：点击项切换选中/取消，其余保留
      return { key: opt.key, text: opt.text, selected: i === oIdx ? !opt.selected : opt.selected }
    })
    this.setData({ ['questions[' + qIdx + '].options']: options })
  },
  onQuestionNav(e) {
    const index = e.currentTarget.dataset.index
    this.setData({ currentIndex: index })
  },
  onSubmit() {
    if (!this.data.questions.length) return
    ensureUser().then(u => {
      const answers = this.data.questions.map(q => ({
        question_id: q.id,
        my_answer: q.options.filter(o => o.selected).map(o => o.key).sort().join('')
      }))
      wx.showLoading({ title: '判分中', mask: true })
      return request('/api/submit', 'POST', {
        user_id: u.user_id, title: '在线练习', time_used: '--', answers: answers
      })
    }).then(data => {
      wx.hideLoading()
      wx.setStorageSync('last_submit', data)
      wx.navigateTo({ url: '/pages/result/result' })
    }).catch(() => {
      wx.hideLoading()
      wx.showToast({ title: '提交失败', icon: 'none' })
    })
  }
})