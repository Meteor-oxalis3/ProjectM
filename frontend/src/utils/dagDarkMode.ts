export  function applyStyles(isDarkMode: any) {
  const vApplication: any = document.querySelector('.workflow'); // 获取 v-application 元素
  const nodes: any = document.querySelectorAll('.vue-flow__node-default');
    // 判断是否为暗黑模式
  if (isDarkMode.value) {
    // 暗黑模式样式
    if (vApplication) {
      vApplication.style.backgroundColor = '#1e1e1e';
    }
    if (nodes) {
      nodes.forEach((node: any) => {
        node.style.border = '1px solid #fff';
        node.style.color = '#fff';
      });
    }
  } else {
    // 恢复默认样式
    if (vApplication) {
      vApplication.style.backgroundColor = '';
    }
    if (nodes) {
      nodes.forEach((node: any) => {
        node.style.border = '';
        node.style.color = '';
      });
    }
  }
};