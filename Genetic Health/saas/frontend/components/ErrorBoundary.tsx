'use client';

import React from 'react';
import { Box, Typography, Button } from '@mui/material';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 4, textAlign: 'center', mt: 8 }}>
          <Typography variant="h1" sx={{ mb: 2 }}>⚠️</Typography>
          <Typography variant="h5" color="error" fontWeight={700} gutterBottom>
            Failed to load dashboard
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 4, maxWidth: 400, mx: 'auto' }}>
            {this.state.error?.message || 'An unexpected error occurred while fetching your genetic data.'}
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => window.location.reload()}
            sx={{ textTransform: 'none', borderRadius: 2 }}
          >
            Refresh Dashboard
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
