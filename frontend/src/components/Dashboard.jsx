import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import WordCloud from './WordCloud'

const SENTIMENT_COLORS = {
  positive: '#4fb286',
  negative: '#e0637a',
  neutral: '#7f86ad',
}

export default function Dashboard({ data }) {
  if (!data) return null

const { product, total_reviews, sentiment_distribution, top_positive_features,
        top_negative_features, word_frequencies_by_sentiment, summary, recommendation } = data

  const pieData = [
    { name: 'Positive', value: sentiment_distribution.positive, key: 'positive' },
    { name: 'Negative', value: sentiment_distribution.negative, key: 'negative' },
    { name: 'Neutral', value: sentiment_distribution.neutral, key: 'neutral' },
  ]

  const pct = (n) => (total_reviews ? Math.round((n / total_reviews) * 100) : 0)

  return (
    <div>
      <div className="card">
        <span className="eyebrow">Dashboard</span>
        <h1 style={{ margin: '4px 0 20px' }}>{product.name}</h1>

        <div className="stat-row">
          <div className="stat">
            <div className="value">{total_reviews}</div>
            <div className="label">Reviews Analyzed</div>
          </div>
          <div className="stat positive">
            <div className="value">{pct(sentiment_distribution.positive)}%</div>
            <div className="label">Positive</div>
          </div>
          <div className="stat negative">
            <div className="value">{pct(sentiment_distribution.negative)}%</div>
            <div className="label">Negative</div>
          </div>
          <div className="stat neutral">
            <div className="value">{pct(sentiment_distribution.neutral)}%</div>
            <div className="label">Neutral</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Customer Opinion Summary</h3>
        <p className="summary-text">{summary}</p>
      </div>
    <div className="card recommendation-card">
  <span className="eyebrow">AI Insight</span>
  <h3>Product Recommendation</h3>
  <p className="summary-text">
    {recommendation || 'No product recommendation available.'}
  </p>
</div>  
      <div className="grid-2">
        <div className="card">
          <h3>Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={3}>
                {pieData.map((entry) => (
                  <Cell key={entry.key} fill={SENTIMENT_COLORS[entry.key]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#222636', border: '1px solid #2d3148' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Top Praised Features</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={top_positive_features} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3148" horizontal={false} />
              <XAxis type="number" stroke="#9497ad" fontSize={12} />
              <YAxis type="category" dataKey="feature" stroke="#9497ad" fontSize={12} width={90} />
              <Tooltip contentStyle={{ background: '#222636', border: '1px solid #2d3148' }} />
              <Bar dataKey="count" fill="#4fb286" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3>Top Complained-About Features</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={top_negative_features} layout="vertical" margin={{ left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3148" horizontal={false} />
            <XAxis type="number" stroke="#9497ad" fontSize={12} />
            <YAxis type="category" dataKey="feature" stroke="#9497ad" fontSize={12} width={90} />
            <Tooltip contentStyle={{ background: '#222636', border: '1px solid #2d3148' }} />
            <Bar dataKey="count" fill="#e0637a" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Positive Word Cloud</h3>
          <WordCloud words={word_frequencies_by_sentiment.positive} colorVar="--positive" />
        </div>
        <div className="card">
          <h3>Negative Word Cloud</h3>
          <WordCloud words={word_frequencies_by_sentiment.negative} colorVar="--negative" />
        </div>
      </div>
    </div>
  )
}
