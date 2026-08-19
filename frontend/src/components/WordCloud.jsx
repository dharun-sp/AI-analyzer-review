export default function WordCloud({ words, colorVar = '--text-dim' }) {
  if (!words || words.length === 0) {
    return <div className="empty-state">Not enough data yet.</div>
  }

  const max = Math.max(...words.map((w) => w.value))
  const min = Math.min(...words.map((w) => w.value))
  const range = max - min || 1

  const sizeFor = (value) => {
    const minSize = 13
    const maxSize = 34
    return minSize + ((value - min) / range) * (maxSize - minSize)
  }

  const opacityFor = (value) => {
    const minOp = 0.55
    const maxOp = 1
    return minOp + ((value - min) / range) * (maxOp - minOp)
  }

  return (
    <div className="wordcloud">
      {words.map((w) => (
        <span
          key={w.text}
          style={{
            fontSize: `${sizeFor(w.value)}px`,
            opacity: opacityFor(w.value),
            fontWeight: w.value > (min + max) / 2 ? 700 : 500,
            color: `var(${colorVar})`,
          }}
          title={`${w.text}: ${w.value} mentions`}
        >
          {w.text}
        </span>
      ))}
    </div>
  )
}
