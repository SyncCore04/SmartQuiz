Page({
  data: {
    searchValue: '',
    categories: [
      { id: 1, name: '语文', count: 520, desc: '古诗词、阅读理解、作文', icon: 'notes-o', accentColor: '#4F46E5', bgColor: '#ede9fe' },
      { id: 2, name: '数学', count: 380, desc: '函数、几何、概率统计', icon: 'chart-trending-o', accentColor: '#EC4899', bgColor: '#fce7f3' },
      { id: 3, name: '英语', count: 450, desc: '阅读、完形、语法词汇', icon: 'comment-o', accentColor: '#F59E0B', bgColor: '#fef3c7' },
      { id: 4, name: '物理', count: 290, desc: '力学、电磁学、光学', icon: 'points', accentColor: '#10B981', bgColor: '#d1fae5' },
      { id: 5, name: '化学', count: 310, desc: '有机化学、无机化学、实验', icon: 'gift-o', accentColor: '#EF4444', bgColor: '#fee2e2' },
      { id: 6, name: '生物', count: 260, desc: '细胞、遗传、生态', icon: 'flower-o', accentColor: '#06B6D4', bgColor: '#cffafe' },
      { id: 7, name: '历史', count: 340, desc: '中国史、世界史、文化史', icon: 'clock-o', accentColor: '#8B5CF6', bgColor: '#ede9fe' },
      { id: 8, name: '地理', count: 220, desc: '自然地理、人文地理', icon: 'location-o', accentColor: '#F97316', bgColor: '#ffedd5' }
    ]
  },
  onLoad() {},
  onSearchInput(e) {
    this.setData({ searchValue: e.detail.value })
  },
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question-list/question-list?categoryId=' + id })
  }
})
