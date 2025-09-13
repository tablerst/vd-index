// 计算百分比，四舍五入到1位小数
export function calcPercent(total: number, value: number): number {
  if (!total || total <= 0) return 0
  return Math.round((value / total) * 1000) / 10
}

// 求和工具
export function sumVotes(values: Array<{ votes: number }>): number {
  return values.reduce((acc, v) => acc + (v?.votes || 0), 0)
}

// 简单的节流函数（用于输入搜索）
export function throttle<T extends (...args: any[]) => void>(fn: T, wait = 300): T {
  let last = 0
  let timer: number | null = null
  return function(this: any, ...args: any[]) {
    const now = Date.now()
    const remaining = wait - (now - last)
    if (remaining <= 0) {
      if (timer) {
        clearTimeout(timer)
        timer = null
      }
      last = now
      fn.apply(this, args)
    } else if (!timer) {
      timer = window.setTimeout(() => {
        last = Date.now()
        timer = null
        fn.apply(this, args)
      }, remaining)
    }
  } as T
}



