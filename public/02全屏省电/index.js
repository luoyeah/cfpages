// 全屏请求函数
function requestFullscreen() {
  const el = document.documentElement;

  // 封装所有浏览器的前缀方法
  const requestMethods = [
    "requestFullscreen",
    "mozRequestFullScreen",
    "webkitRequestFullscreen",
    "msRequestFullscreen",
  ];

  // 尝试触发全屏
  for (const method of requestMethods) {
    if (el[method]) {
      return el[method]().catch((err) => {
        updateStatus(`全屏失败: ${err.message}`, false);
      });
    }
  }

  updateStatus("您的浏览器不支持全屏API", false);
}

// 页面加载完成后执行
window.addEventListener("load", () => {
  let body = document.getElementsByTagName("body")[0];

  body.addEventListener("click", () => {
    requestFullscreen();
  });

  // 防止F11等快捷键干扰
  // window.addEventListener('keydown', (e) => {
  //     if (e.key === 'F11') {
  //         e.preventDefault();
  //         updateStatus("已阻止退出全屏", true);
  //     }
  // });

  // 防止右键菜单
  document.addEventListener("contextmenu", (e) => {
    e.preventDefault();
  });
});
