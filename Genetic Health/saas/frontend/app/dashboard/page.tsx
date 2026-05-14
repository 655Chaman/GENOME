import { SuspenseLoader } from '~components/SuspenseLoader';
import { ErrorBoundary } from '~components/ErrorBoundary';
import { DashboardView } from '~features/reports/components/Dashboard';

export default function DashboardPage() {
  return (
    <ErrorBoundary>
      <SuspenseLoader>
        <DashboardView />
      </SuspenseLoader>
    </ErrorBoundary>
  );
}
