import TransactionTable from '../components/TransactionTable';
import AlertPanel from '../components/AlertPanel';
import RiskChart from '../components/RiskChart';

export default function Dashboard() {
  return (
    <div>
      <h1>Fraud Detection Dashboard</h1>
      <AlertPanel />
      <TransactionTable />
      <RiskChart />
    </div>
  );
}