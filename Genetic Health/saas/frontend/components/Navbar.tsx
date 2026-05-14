'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth, UserButton, SignOutButton } from '@clerk/nextjs';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import BiotechIcon from '@mui/icons-material/Biotech';
import BugReportIcon from '@mui/icons-material/BugReport';
import ShieldIcon from '@mui/icons-material/Shield';

export default function Navbar() {
  const { isSignedIn } = useAuth();

  return (
    <AppBar position="sticky" elevation={0} sx={{ 
      background: 'rgba(3, 3, 5, 0.8)', 
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid',
      borderColor: 'divider',
      zIndex: (theme) => theme.zIndex.drawer + 1
    }}>
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between', height: 72 }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1.5, 
            textDecoration: 'none', 
            color: 'inherit',
            cursor: 'pointer'
          }} component={Link} href="/">
            <BiotechIcon sx={{ color: 'primary.main', fontSize: 32 }} />
            <Typography variant="h6" fontWeight={900} letterSpacing="-0.03em" sx={{ display: { xs: 'none', sm: 'block' } }}>
              GENOME
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 3 } }}>
            {!isSignedIn ? (
              <>
                <Link href="/sign-in" style={{ textDecoration: 'none' }}>
                  <Button variant="text" sx={{ textTransform: 'none', fontWeight: 600, color: 'text.secondary' }}>
                    Sign In
                  </Button>
                </Link>
                <Link href="/sign-up" style={{ textDecoration: 'none' }}>
                  <Button variant="contained" sx={{ textTransform: 'none', fontWeight: 600, px: 3, borderRadius: 2 }}>
                    Get Started
                  </Button>
                </Link>
              </>
            ) : (
              <>
                <Link href="/dashboard" style={{ textDecoration: 'none' }}>
                  <Button variant="text" sx={{ textTransform: 'none', fontWeight: 600, color: 'text.secondary' }}>
                    Dashboard
                  </Button>
                </Link>
                <Link href="/dashboard/outbreak" style={{ textDecoration: 'none' }}>
                  <Button
                    variant="text"
                    startIcon={<BugReportIcon fontSize="small" />}
                    sx={{ textTransform: 'none', fontWeight: 600, color: 'text.secondary', display: { xs: 'none', md: 'inline-flex' } }}
                  >
                    Outbreak
                  </Button>
                </Link>
                <Link href="/dashboard/personalized-risk" style={{ textDecoration: 'none' }}>
                  <Button
                    variant="text"
                    startIcon={<ShieldIcon fontSize="small" />}
                    sx={{ textTransform: 'none', fontWeight: 600, color: 'text.secondary', display: { xs: 'none', md: 'inline-flex' } }}
                  >
                    My Risk
                  </Button>
                </Link>
                <SignOutButton signOutUrl="/">
                  <Button variant="text" sx={{ textTransform: 'none', fontWeight: 600, color: 'text.secondary' }}>
                    Sign Out
                  </Button>
                </SignOutButton>
                <UserButton afterSignOutUrl="/" />
              </>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
