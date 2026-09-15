Page({
  data: {
    swiperList: [
      {
        id: 1,
        image: '/images/photo-1517673132405-a56a62b18caf_w1080.jpg',
        title: '每日刷题挑战'
      },
      {
        id: 2,
        image: '/images/photo-1564609116494-380be7238d7d_w1080.jpg',
        title: '模拟考试上线'
      }
    ],
    categories: [
      { id: 1, name: '语文', icon: 'notes-o', count: 520, color: '#4F46E5', bgColor: '#ede9fe' },
      { id: 2, name: '数学', icon: 'chart-trending-o', count: 380, color: '#EC4899', bgColor: '#fce7f3' },
      { id: 3, name: '英语', icon: 'comment-o', count: 450, color: '#F59E0B', bgColor: '#fef3c7' },
      { id: 4, name: '理综', icon: 'points', count: 290, color: '#10B981', bgColor: '#d1fae5' }
    ],
    hotBanks: [
      {
        id: 1,
        title: '2024高考语文真题精选',
        desc: '涵盖近五年高考语文真题，精选阅读理解与作文素材',
        count: 120,
        joined: 3280,
        tag: '热门',
        image: '/images/photo-1685287731216-a7a0fae7a41a_w400.jpg'
      },
      {
        id: 2,
        title: '数学压轴题专项突破',
        desc: '针对高考数学最后两道大题的专项训练',
        count: 80,
        joined: 2156,
        tag: '推荐',
        image: '/images/photo-1495465798138-718f86d1a4bc_w400.jpg'
      },
      {
        id: 3,
        title: '英语完形填空强化训练',
        desc: '高频词汇与经典题型，快速提升完形填空得分',
        count: 95,
        joined: 1890,
        tag: '新课',
        image: '/images/photo-1617239098289-ad0ee436361e_w400.jpg'
      }
    ],
    notice: '系统将于本周六进行维护升级，届时部分功能暂不可用，敬请谅解。',
    recentPractices: [
      { id: 1, title: '语文古诗词默写', score: 85, total: 100, date: '2024-01-15', icon: 'notes-o', bgColor: '#ede9fe', iconColor: '#4F46E5' },
      { id: 2, title: '数学函数专题', score: 72, total: 100, date: '2024-01-14', icon: 'chart-trending-o', bgColor: '#fce7f3', iconColor: '#EC4899' },
      { id: 3, title: '英语阅读理解', score: 90, total: 100, date: '2024-01-13', icon: 'comment-o', bgColor: '#fef3c7', iconColor: '#F59E0B' }
    ]
  },
  onLoad() {},
  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
  },
  onSearch() {
    wx.navigateTo({ url: '/pages/category/category' })
  },
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question-list/question-list?categoryId=' + id })
  },
  onHotBankTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question-list/question-list?bankId=' + id })
  },
  onPracticeTap() {
    wx.navigateTo({ url: '/pages/answer/answer' })
  }
})
