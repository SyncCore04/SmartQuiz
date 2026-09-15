// 统一的网络请求与游客登录工具
// 真机演示时，把 BASE_URL 改成电脑的局域网 IP，如 http://192.168.1.100:5000
const BASE_URL = 'http://127.0.0.1:5000'
const USER_KEY = 'smartquiz_user'

function request(path, method = 'GET', data = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + path,
      method: method,
      data: data,
      success(res) {
        const r = res.data
        if (r && r.code === 0) {
          resolve(r.data)
        } else {
          reject(r || { msg: '请求失败' })
        }
      },
      fail: reject
    })
  })
}

// 游客登录（假账号）：传昵称，返回 userId
function login(nickname = '张磊学长') {
  return request('/api/login', 'POST', { nickname }).then(d => {
    wx.setStorageSync(USER_KEY, d)
    return d
  })
}

// 确保已有用户身份。
// 始终向后端发起一次幂等登录：后端按 nickname 复用同一用户，
// 因此能拿到当前库中最新有效的 user_id，避免本地缓存过期导致取不到数据。
function ensureUser() {
  const u = wx.getStorageSync(USER_KEY)
  const nickname = (u && u.nickname) ? u.nickname : '张磊学长'
  return login(nickname)
}

// 获取当前 user_id（可能为空，需先 ensureUser）
function getUserId() {
  const u = wx.getStorageSync(USER_KEY)
  return u ? u.user_id : ''
}

module.exports = { BASE_URL, request, login, ensureUser, getUserId }