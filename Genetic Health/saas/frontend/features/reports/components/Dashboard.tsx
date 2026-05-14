'use client';

import React, { useCallback } from 'react';
import { useUser, SignOutButton } from '@clerk/nextjs';
import { useSuspenseQuery, useQueryClient } from '@tanstack/react-query';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { reportsApi } from '../api/reportsApi';
import { ReportCard } from './ReportCard';
import { UploadReport } from './UploadReport';

export const DashboardView: React.FC = () => {
  const { user } = useUser();
  const queryClient = useQueryClient();
  const firstName = user?.firstName ?? 'there';

  const { data: reports } = useSuspenseQuery({
    queryKey: ['reports'],
    queryFn: reportsApi.getReports,
  });

  const handleDelete = useCallback(async (id: string) => {
    try {
      await reportsApi.deleteReport(id);
      queryClient.setQueryData(['reports'], (old: any) => 
        old ? old.filter((r: any) => r.id !== id) : []
      );
    } catch (err) {
      console.error(err);
      alert('Failed to delete report');
    }
  }, [queryClient]);

  const refreshReports = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['reports'] });
  }, [queryClient]);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: { xs: 2, md: 4 } }}>
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
            Hey, {firstName} 👋
          </Typography>
          <SignOutButton signOutUrl="/">
            <Button size="small" variant="outlined" color="inherit" sx={{ opacity: 0.7, '&:hover': { opacity: 1 } }}>
              Sign Out
            </Button>
          </SignOutButton>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Your genetic health reports, all in one place.
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 5 }}>
        {[
          { label: 'Total Reports', value: reports.length },
          { label: 'Disease Risk', value: reports.filter(r => r.report_type === 'disease_risk').length },
          { label: 'Genetic Profiles', value: reports.filter(r => r.report_type === 'genetic').length },
          { label: 'Protocols', value: reports.filter(r => r.report_type === 'protocol').length },
        ].map((stat, i) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
            <Paper sx={{ p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="overline" color="text.secondary" fontWeight={600} display="block" gutterBottom>
                {stat.label}
              </Typography>
              <Typography variant="h3" fontWeight={700}>
                {stat.value}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <UploadReport onSaved={refreshReports} />

      {reports.length === 0 ? (
        <Paper sx={{ p: 8, textAlign: 'center', borderRadius: 3, border: '1px dashed', borderColor: 'divider', bgcolor: 'transparent' }}>
          <Typography variant="h2" sx={{ mb: 2 }}>🧬</Typography>
          <Typography variant="h6" gutterBottom>No reports yet</Typography>
          <Typography color="text.secondary">
            Click &quot;Analyze New Genome&quot; above to save your first genetic health report.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {reports.map((r) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={r.id}>
              <ReportCard report={r} onDelete={handleDelete} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};
