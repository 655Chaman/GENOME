import type { Report } from '~features/reports/types/report';

export const reportsApi = {
  getReports: async (): Promise<Report[]> => {
    const res = await fetch('/api/reports');
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },
  deleteReport: async (id: string): Promise<void> => {
    const res = await fetch(`/api/reports/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete report');
  }
};
