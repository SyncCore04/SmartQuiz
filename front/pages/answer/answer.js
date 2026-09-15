Page({
  data: {
    currentIndex: 0,
    questions: [
      {
        id: 1, type: '单选', title: '下列词语中，没有错别字的一组是？',
        options: [
          { key: 'A', text: '鬼鬼祟祟', selected: false },
          { key: 'B', text: '再接再厉', selected: false },
          { key: 'C', text: '金壁辉煌', selected: false },
          { key: 'D', text: '哀声叹气', selected: false }
        ]
      },
      {
        id: 2, type: '单选', title: '已知函数 f(x) = x³ - 3x + 1，则 f(x) 的极小值为？',
        options: [
          { key: 'A', text: '-1', selected: false },
          { key: 'B', text: '3', selected: false },
          { key: 'C', text: '-3', selected: false },
          { key: 'D', text: '1', selected: false }
        ]
      },
      {
        id: 3, type: '单选', title: 'The teacher asked us to ______ the homework before Friday.',
        options: [
          { key: 'A', text: 'finish', selected: false },
          { key: 'B', text: 'finishing', selected: false },
          { key: 'C', text: 'finished', selected: false },
          { key: 'D', text: 'finishes', selected: false }
        ]
      },
      {
        id: 4, type: '单选', title: '下列文学作品与其作者对应正确的是？',
        options: [
          { key: 'A', text: '《红楼梦》- 施耐庵', selected: false },
          { key: 'B', text: '《西游记》- 吴承恩', selected: false },
          { key: 'C', text: '《三国演义》- 曹雪芹', selected: false },
          { key: 'D', text: '《水浒传》- 罗贯中', selected: false }
        ]
      },
      {
        id: 5, type: '单选', title: '地球是太阳系中最大的行星。此说法是否正确？',
        options: [
          { key: 'A', text: '正确', selected: false },
          { key: 'B', text: '错误', selected: false },
          { key: 'C', text: '不确定', selected: false },
          { key: 'D', text: '以上都不对', selected: false }
        ]
      },
      {
        id: 6, type: '单选', title: '水在标准大气压下的沸点是多少？',
        options: [
          { key: 'A', text: '90°C', selected: false },
          { key: 'B', text: '100°C', selected: false },
          { key: 'C', text: '110°C', selected: false },
          { key: 'D', text: '120°C', selected: false }
        ]
      },
      {
        id: 7, type: '单选', title: '光合作用主要发生在植物的哪个部位？',
        options: [
          { key: 'A', text: '根部', selected: false },
          { key: 'B', text: '茎部', selected: false },
          { key: 'C', text: '叶片', selected: false },
          { key: 'D', text: '花朵', selected: false }
        ]
      },
      {
        id: 8, type: '单选', title: '化学反应 2H₂ + O₂ → 2H₂O 中，生成物是什么？',
        options: [
          { key: 'A', text: '氢气', selected: false },
          { key: 'B', text: '氧气', selected: false },
          { key: 'C', text: '水', selected: false },
          { key: 'D', text: '二氧化碳', selected: false }
        ]
      },
      {
        id: 9, type: '单选', title: '唐朝的开国皇帝是谁？',
        options: [
          { key: 'A', text: '李世民', selected: false },
          { key: 'B', text: '李渊', selected: false },
          { key: 'C', text: '李隆基', selected: false },
          { key: 'D', text: '武则天', selected: false }
        ]
      },
      {
        id: 10, type: '单选', title: '赤道是地球上最长的纬线，它的周长约为？',
        options: [
          { key: 'A', text: '2万公里', selected: false },
          { key: 'B', text: '4万公里', selected: false },
          { key: 'C', text: '6万公里', selected: false },
          { key: 'D', text: '8万公里', selected: false }
        ]
      }
    ]
  },
  onLoad() {},
  onOptionTap(e) {
    const qIdx = e.currentTarget.dataset.qindex
    const oIdx = e.currentTarget.dataset.oindex
    const key = 'questions[' + qIdx + '].options'
    const options = this.data.questions[qIdx].options.map(function(opt, i) {
      return { key: opt.key, text: opt.text, selected: i === oIdx }
    })
    this.setData({ [key]: options })
  },
  onQuestionNav(e) {
    const index = e.currentTarget.dataset.index
    this.setData({ currentIndex: index })
  },
  onSubmit() {
    wx.navigateTo({ url: '/pages/result/result' })
  }
})
