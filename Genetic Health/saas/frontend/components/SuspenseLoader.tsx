'use client';

import React from 'react';
import { Box, CircularProgress } from '@mui/material';

export const SuspenseLoader: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <React.Suspense fallback={
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    }>
      {children}
    </React.Suspense>
  );
};
