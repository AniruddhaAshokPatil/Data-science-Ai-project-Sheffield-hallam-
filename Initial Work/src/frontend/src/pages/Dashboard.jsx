import TransactionTable from '../components/TransactionTable';
import AlertPanel from '../components/AlertPanel';
import RiskChart from '../components/RiskChart';

export default function Dashboard() {
  return (
    <div>
      {/* I keep this page as a simple composition layer that brings together
          several UI components into one dashboard view. */}
      <h1>Fraud Detection Dashboard</h1>
      <AlertPanel />
      <TransactionTable />
      <RiskChart />
    </div>
  );
}
