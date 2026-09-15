Page({
  data: {
    exams: [
      {
        id: 1,
        title: '2024年高考语文模拟考试',
        cover: '/images/photo-1685287731216-a7a0fae7a41a_w400.jpg',
        date: '2024-03-15',
        duration: '120分钟',
        totalCount: 50,
        joined: 1256,
        status: '进行中',
        statusColor: '#4F46E5'
      },
      {
        id: 2,
        title: '数学函数与导数专项考试',
        cover: '/images/photo-1495465798138-718f86d1a4bc_w400.jpg',
        date: '2024-03-20',
        duration: '90分钟',
        totalCount: 30,
        joined: 890,
        status: '未开始',
        statusColor: '#FFD166'
      },
      {
        id: 3,
        title: '英语综合能力测评',
        cover: '/images/photo-1617239098289-ad0ee436361e_w400.jpg',
        date: '2024-03-10',
        duration: '100分钟',
        totalCount: 45,
        joined: 2100,
        status: '已结束',
        statusColor: '#999'
      },
      {
        id: 4,
        title: '理综全真模拟考试',
        cover: '/images/photo-1617529497832-5ad49d9b5928_w400.jpg',
        date: '2024-04-01',
        duration: '150分钟',
        totalCount: 60,
        joined: 680,
        status: '未开始',
        statusColor: '#FFD166'
      }
    ]
  },
  onLoad() {},
  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
  },
  onExamTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/exam-detail/exam-detail?examId=' + id })
  }
})
