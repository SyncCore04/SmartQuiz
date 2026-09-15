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
    questions: [
      { id: 1, num: 1, type: '单选', typeKey: 'single', difficulty: '简单', title: '下列词语中，没有错别字的一组是？', options: 'A. 鬼鬼祟祟 B. 再接再厉 C. 金壁辉煌 D. 哀声叹气' },
      { id: 2, num: 2, type: '多选', typeKey: 'multi', difficulty: '中等', title: '下列关于光合作用的叙述，正确的是？', options: 'A. 光反应在叶绿体类囊体薄膜上进行' },
      { id: 3, num: 3, type: '判断', typeKey: 'judge', difficulty: '简单', title: '地球是太阳系中最大的行星。', options: '正确 / 错误' },
      { id: 4, num: 4, type: '单选', typeKey: 'single', difficulty: '困难', title: '已知函数 f(x) = x³ - 3x + 1，则 f(x) 的极小值为？', options: 'A. -1 B. 3 C. -3 D. 1' },
      { id: 5, num: 5, type: '填空', typeKey: 'fill', difficulty: '中等', title: 'The teacher asked us to ______ (完成) the homework before Friday.', options: '' },
      { id: 6, num: 6, type: '单选', typeKey: 'single', difficulty: '中等', title: '下列文学作品与其作者对应正确的是？', options: 'A.《红楼梦》-施耐庵 B.《西游记》-吴承恩' },
      { id: 7, num: 7, type: '多选', typeKey: 'multi', difficulty: '困难', title: '关于电磁感应现象，下列说法正确的是？', options: 'A. 闭合回路中的磁通量变化会产生感应电流' },
      { id: 8, num: 8, type: '判断', typeKey: 'judge', difficulty: '简单', title: '水在标准大气压下的沸点是100°C。', options: '正确 / 错误' },
      { id: 9, num: 9, type: '单选', typeKey: 'single', difficulty: '困难', title: '若等差数列{an}的前n项和为Sn，已知S10=100，则a5+a6=?', options: 'A. 10 B. 20 C. 15 D. 25' },
      { id: 10, num: 10, type: '填空', typeKey: 'fill', difficulty: '中等', title: '化学反应 2H₂ + O₂ → 2H₂O 中，反应物是____。', options: '' }
    ]
  },
  onLoad() {},
  onFilterTap(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ activeFilter: key })
  },
  onQuestionTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/answer/answer?questionId=' + id })
  }
})
