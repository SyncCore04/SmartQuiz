const { request } = require('../../utils/api')

Page({
  data: {
    searchValue: '',
    categories: [],
    allCats: []
  },
  onLoad() {
    request('/api/categories').then(cats => {
      const mapped = (cats || []).map(c => ({
        id: c.id, name: c.name, count: c.count, icon: c.icon,
        accentColor: c.color, bgColor: c.bgColor, desc: ''
      }))
      this.setData({ categories: mapped, allCats: mapped })
    }).catch(() => {})
  },
  onSearchInput(e) {
    const v = e.detail.value
    this.setData({
      searchValue: v,
      categories: v ? this.data.allCats.filter(c => c.name.indexOf(v) > -1) : this.data.allCats
    })
  },
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question-list/question-list?categoryId=' + id })
  }
})