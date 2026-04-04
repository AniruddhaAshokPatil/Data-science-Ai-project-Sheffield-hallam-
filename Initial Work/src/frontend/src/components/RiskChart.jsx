import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function RiskChart() {
  // I keep temporary dummy data here because this component is still a UI
  // placeholder for a future live risk trend chart.
  const data = [
    { timestamp: '10:00', risk: 0.1 },
    { timestamp: '10:05', risk: 0.85 },
    { timestamp: '10:10', risk: 0.05 },
    { timestamp: '10:15', risk: 0.4 }
  ];

  return (
    <div>
      <h2>Risk Chart</h2>
      <LineChart width={500} height={250} data={data}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="risk" stroke="#8884d8" />
      </LineChart>
    </div>
  );
}
