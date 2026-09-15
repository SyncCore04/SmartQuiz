Component({
  data: {
    selected: 0,
    color: "#999999",
    selectedColor: "#4F46E5",
    list: [
      {
        pagePath: "/pages/index/index",
        text: "首页",
        icon: "home-o"
      },
      {
        pagePath: "/pages/exam-list/exam-list",
        text: "考试",
        icon: "todo-list-o"
      },
      {
        pagePath: "/pages/profile/profile",
        text: "我的",
        icon: "user-o"
      }
    ]
  },
  methods: {
    switchTab(e) {
      const data = e.currentTarget.dataset
      const url = data.path
      wx.switchTab({ url })
    }
  }
})
