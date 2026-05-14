'use client';

import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/nextjs';
import {
  Box, Container, Typography, Grid, Paper, Chip,
  CircularProgress, Alert, Fade, List, ListItem,
  ListItemIcon, ListItemText, Divider, LinearProgress
} from '@mui/material';
import DnaIcon from '@mui/icons-material/Biotech';
import GppBadIcon from '@mui/icons-material/GppBad';
import GppGoodIcon from '@mui/icons-material/GppGood';
import GppMaybeIcon from '@mui/icons-material/GppMaybe';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8001';

interface PersonalizedData {
  personalized_score: number;
  threat_level: 'CRITICAL' | 'ELEVATED' | 'STANDARD';
  genetic_factors_considered: string[];
  recommended_protocols: string[];
  outbreak_context: string[];
}

const THREAT_CONFIG = {
  CRITICAL: {
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.08)',
    border: 'rgba(239,68,68,0.25)',
    icon: <GppBadIcon sx={{ fontSize: 48 }} />,
    label: 'CRITICAL THREAT',
    description: 'Your genetic profile significantly amplifies the current regional risk. Immediate action is recommended.',
  },
  ELEVATED: {
    color: '#f97316',
    bg: 'rgba(249,115,22,0.08)',
    border: 'rgba(249,115,22,0.25)',
    icon: <GppMaybeIcon sx={{ fontSize: 48 }} />,
    label: 'ELEVATED RISK',
    description: 'Your genetics moderate the regional risk. Take precautionary measures and stay alert.',
  },
  STANDARD: {
    color: '#22c55e',
    bg: 'rgba(34,197,94,0.08)',
    border: 'rgba(34,197,94,0.25)',
    icon: <GppGoodIcon sx={{ fontSize: 48 }} />,
    label: 'STANDARD RISK',
    description: 'No significant genetic amplification detected. Maintain standard health precautions.',
  },
};

function ThreatBanner({ level, score }: { level: keyof typeof THREAT_CONFIG; score: number }) {
  const cfg = THREAT_CONFIG[level];
  return (
    <Paper sx={{
      p: 4, borderRadius: 4, mb: 3,
      background: cfg.bg,
      border: `1px solid ${cfg.border}`,
      display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap'
    }}>
      <Box sx={{ color: cfg.color }}>{cfg.icon}</Box>
      <Box sx={{ flex: 1 }}>
        <Chip label={cfg.label} sx={{
          fontWeight: 800, letterSpacing: '0.12em', mb: 1,
          bgcolor: cfg.color + '22', color: cfg.color, border: `1px solid ${cfg.color}44`
        }} />
        <Typography variant="body1" color="text.secondary">{cfg.description}</Typography>
      </Box>
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h2" fontWeight={900} sx={{ color: cfg.color, lineHeight: 1 }}>
          {Math.round(score)}
        </Typography>
        <Typography variant="caption" color="text.secondary" fontWeight={600}>PERSONAL SCORE /100</Typography>
      </Box>
    </Paper>
  );
}

export default function PersonalizedRiskPage() {
  const { user, isLoaded } = useUser();
  const [data, setData] = useState<PersonalizedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoaded) return;
    // Use the Clerk user ID — mapped to 'user_high_risk' or 'user_medium_risk' via fusion_engine for MVP
    const userId = user?.id ?? 'anonymous';
    fetch(`${BACKEND_URL}/api/outbreak/personalized?user_id=${encodeURIComponent(userId)}`)
      .then(res => {
        if (!res.ok) throw new Error(`Backend error: ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [isLoaded, user]);

  return (
    <Container maxWidth="lg" sx={{ py: 5 }}>
      {/* Header */}
      <Fade in timeout={500}>
        <Box sx={{ mb: 5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
            <DnaIcon sx={{ color: 'primary.main' }} />
            <Typography variant="overline" color="primary.main" fontWeight={700} letterSpacing="0.15em">
              PERSONALIZED INTELLIGENCE
            </Typography>
          </Box>
          <Typography variant="h3" component="h1" fontWeight={800} letterSpacing="-0.03em" gutterBottom>
            Your Personal Threat Level
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
            This assessment <strong>fuses the current Bangalore Dengue outbreak risk</strong> with
            your unique genomic profile to compute a severity score tailored specifically to you.
          </Typography>
        </Box>
      </Fade>

      {(loading || !isLoaded) && (
        <Box sx={{ py: 10, textAlign: 'center' }}>
          <CircularProgress size={48} />
          <Typography color="text.secondary" sx={{ mt: 2 }}>
            Fusing outbreak data with your genetic profile…
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="warning" sx={{ borderRadius: 3, mb: 4 }}>
          <strong>Backend unavailable.</strong> {error}. Make sure the FastAPI server is running on port 8001.
        </Alert>
      )}

      {data && (
        <Fade in timeout={700}>
          <Box>
            {/* Threat Banner */}
            <ThreatBanner level={data.threat_level} score={data.personalized_score} />

            <Grid container spacing={3}>

              {/* Genetic Factors */}
              <Grid size={{ xs: 12, md: 5 }}>
                <Paper sx={{
                  p: 4, borderRadius: 4, height: '100%',
                  border: '1px solid', borderColor: 'divider',
                  background: 'rgba(255,255,255,0.03)'
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
                    <DnaIcon sx={{ color: 'primary.main' }} />
                    <Typography variant="h6" fontWeight={700}>
                      Genetic Factors Considered
                    </Typography>
                  </Box>
                  {data.genetic_factors_considered.length > 0 ? (
                    <>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        The following SNPs from your genome were identified as relevant to this assessment:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {data.genetic_factors_considered.map((snp, i) => (
                          <Chip key={i} label={snp} size="small" sx={{
                            fontFamily: 'monospace', fontSize: '0.75rem',
                            bgcolor: 'rgba(99,102,241,0.12)',
                            color: 'primary.light',
                            border: '1px solid rgba(99,102,241,0.25)'
                          }} />
                        ))}
                      </Box>
                      <Divider sx={{ my: 3 }} />
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <LinearProgress
                          variant="determinate"
                          value={data.personalized_score}
                          sx={{
                            flex: 1, height: 8, borderRadius: 2,
                            bgcolor: 'rgba(255,255,255,0.06)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: THREAT_CONFIG[data.threat_level].color,
                              borderRadius: 2
                            }
                          }}
                        />
                        <Typography variant="body2" fontWeight={700} sx={{ whiteSpace: 'nowrap' }}>
                          {Math.round(data.personalized_score)} / 100
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Personalized severity score (vs. {Math.round(data.personalized_score / 1.5)} regional baseline)
                      </Typography>
                    </>
                  ) : (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <GppGoodIcon sx={{ fontSize: 40, color: '#22c55e', mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        No high-risk inflammatory or immune SNPs detected in your profile.
                        Your genetic risk for severe Dengue is at baseline.
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Grid>

              {/* Protocols + Context */}
              <Grid size={{ xs: 12, md: 7 }}>
                <Grid container spacing={3} direction="column">

                  {/* Personalized Protocols */}
                  <Grid size={{ xs: 12 }}>
                    <Paper sx={{
                      p: 4, borderRadius: 4,
                      border: '1px solid', borderColor: 'divider',
                      background: 'rgba(255,255,255,0.03)'
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                        <LocalHospitalIcon sx={{ color: 'primary.main' }} />
                        <Typography variant="h6" fontWeight={700}>
                          Your Personalized Protocol
                        </Typography>
                      </Box>
                      <List disablePadding>
                        {data.recommended_protocols.map((protocol, i) => (
                          <ListItem key={i} disablePadding sx={{ mb: 2, alignItems: 'flex-start' }}>
                            <ListItemIcon sx={{ minWidth: 32, mt: 0.5 }}>
                              <CheckCircleOutlineIcon fontSize="small" sx={{ color: 'primary.main' }} />
                            </ListItemIcon>
                            <ListItemText
                              primary={protocol}
                              primaryTypographyProps={{ variant: 'body2', lineHeight: 1.7 }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>

                  {/* Outbreak Context */}
                  <Grid size={{ xs: 12 }}>
                    <Paper sx={{
                      p: 4, borderRadius: 4,
                      border: '1px solid', borderColor: 'divider',
                      background: 'rgba(255,255,255,0.03)'
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                        <WaterDropIcon sx={{ color: '#60a5fa' }} />
                        <Typography variant="h6" fontWeight={700}>
                          Regional Outbreak Context
                        </Typography>
                      </Box>
                      <List disablePadding>
                        {data.outbreak_context.map((ctx, i) => (
                          <ListItem key={i} disablePadding sx={{ mb: 1.5, alignItems: 'flex-start' }}>
                            <ListItemIcon sx={{ minWidth: 32, mt: 0.5 }}>
                              <WaterDropIcon fontSize="small" sx={{ color: '#60a5fa66' }} />
                            </ListItemIcon>
                            <ListItemText
                              primary={ctx}
                              primaryTypographyProps={{ variant: 'body2', color: 'text.secondary', lineHeight: 1.6 }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>

            {/* Disclaimer */}
            <Paper sx={{ p: 3, mt: 3, borderRadius: 3, bgcolor: 'rgba(255,255,255,0.02)', border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary" display="block">
                ⚠️ <strong>Disclaimer:</strong> This personalized risk assessment is for informational purposes only and does not constitute medical advice.
                Genetic risk amplification is a probabilistic model. Consult a physician for clinical guidance.
              </Typography>
            </Paper>
          </Box>
        </Fade>
      )}
    </Container>
  );
}
