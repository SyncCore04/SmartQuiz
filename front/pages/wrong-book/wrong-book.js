const { request, ensureUser } = require('../../utils/api')

Page({
  data: {
    wrongList: []
  },
  onShow() {
    ensureUser().then(u => {
      return request('/api/wrong-book?user_id=' + u.user_id)
    }).then(list => {
      this.setData({ wrongList: list || [] })
    }).catch(() => {})
  }
})