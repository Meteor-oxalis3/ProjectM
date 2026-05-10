export function countObjects(inputData: any): number {
    if (typeof inputData !== 'object' || inputData === null) {
      // 如果当前值不是对象，返回 0
      return 0;
    }
    let count = 1; // 当前对象本身算一个
    // 遍历对象的属性
    for (const key in inputData) {
      if (inputData.hasOwnProperty(key)) {
        // 递归统计子对象的数量
        count += countObjects(inputData[key]);
      }
    }
    return count;
  }

export function generateColors(numColors: number): string[] {
  const colors: string[] = [];

  // 定义起始颜色和结束颜色
  const startColor = { r: 66, g: 205, b: 245 };
  const endColor = { r: 0, g: 10, b: 255 };

  // 根据 numColors 均分颜色
  for (let i = 0; i < numColors; i++) {
    // 计算当前颜色的插值比例
    const ratio = i / (numColors - 1);
    // 计算当前颜色的 RGB 值
    const r = Math.round(startColor.r + (endColor.r - startColor.r) * ratio);
    const g = Math.round(startColor.g + (endColor.g - startColor.g) * ratio);
    const b = Math.round(startColor.b + (endColor.b - startColor.b) * ratio);
    const a = 0.6;
    // 将颜色转换为 rgba 格式
    const rgbaColor = `rgba(${r}, ${g}, ${b}, ${a})`;
    colors.push(rgbaColor);
  }

  return colors;
}