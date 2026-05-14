'use client';

import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Grid, Paper, Chip,
  CircularProgress, Alert, LinearProgress, Divider,
  List, ListItem, ListItemIcon, ListItemText, Fade
} from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import BugReportIcon from '@mui/icons-material/BugReport';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ShieldIcon from '@mui/icons-material/Shield';
import LocationOnIcon from '@mui/icons-material/LocationOn';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8001';

interface OutbreakData {
  predicted_cases: number;
  risk_score: number;
  insights: string[];
}

function RiskGauge({ score }: { score: number }) {
  const color = score > 70 ? '#ef4444' : score > 40 ? '#f97316' : '#22c55e';
  const label = score > 70 ? 'HIGH' : score > 40 ? 'ELEVATED' : 'LOW';

  return (
    <Box sx={{ textAlign: 'center', py: 3 }}>
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress
          variant="determinate"
          value={score}
          size={160}
          thickness={5}
          sx={{ color, '& .MuiCircularProgress-circle': { strokeLinecap: 'round' } }}
        />
        <Box sx={{
          position: 'absolute', inset: 0, display: 'flex',
          flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
        }}>
          <Typography variant="h3" fontWeight={800} sx={{ color, lineHeight: 1 }}>
            {Math.round(score)}
          </Typography>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            / 100
          </Typography>
        </Box>
      </Box>
      <Box sx={{ mt: 2 }}>
        <Chip
          label={label + ' RISK'}
          sx={{
            fontWeight: 700,
            fontSize: '0.85rem',
            bgcolor: color + '22',
            color,
            border: `1px solid ${color}55`,
            letterSpacing: '0.1em'
          }}
        />
      </Box>
    </Box>
  );
}

export default function OutbreakPage() {
  const [data, setData] = useState<OutbreakData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/outbreak/bangalore`)
      .then(res => {
        if (!res.ok) throw new Error(`Backend error: ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Container maxWidth="lg" sx={{ py: 5 }}>
      {/* Header */}
      <Fade in timeout={500}>
        <Box sx={{ mb: 5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
            <LocationOnIcon sx={{ color: 'primary.main' }} />
            <Typography variant="overline" color="primary.main" fontWeight={700} letterSpacing="0.15em">
              OUTBREAK INTELLIGENCE
            </Typography>
          </Box>
          <Typography variant="h3" component="h1" fontWeight={800} letterSpacing="-0.03em" gutterBottom>
            Dengue Risk Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 560 }}>
            Real-time outbreak risk for <strong>Bangalore, India</strong>, powered by a machine-learning model
            trained on environmental and epidemiological patterns.
          </Typography>
        </Box>
      </Fade>

      {loading && (
        <Box sx={{ py: 10, textAlign: 'center' }}>
          <CircularProgress size={48} />
          <Typography color="text.secondary" sx={{ mt: 2 }}>
            Running intelligence model…
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
          <Grid container spacing={3}>

            {/* Risk Gauge */}
            <Grid size={{ xs: 12, md: 4 }}>
              <Paper sx={{
                p: 4, borderRadius: 4, height: '100%',
                border: '1px solid', borderColor: 'divider',
                background: 'rgba(255,255,255,0.03)',
                backdropFilter: 'blur(12px)'
              }}>
                <Typography variant="overline" color="text.secondary" fontWeight={700} display="block" sx={{ mb: 1 }}>
                  Current Risk Score
                </Typography>
                <RiskGauge score={data.risk_score} />
                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography color="text.secondary" variant="body2">Predicted Cases (7d)</Typography>
                  <Typography fontWeight={700} variant="h6">
                    ~{Math.round(data.predicted_cases * 7)}
                  </Typography>
                </Box>
              </Paper>
            </Grid>

            {/* Environmental Indicators */}
            <Grid size={{ xs: 12, md: 4 }}>
              <Paper sx={{
                p: 4, borderRadius: 4, height: '100%',
                border: '1px solid', borderColor: 'divider',
                background: 'rgba(255,255,255,0.03)'
              }}>
                <Typography variant="overline" color="text.secondary" fontWeight={700} display="block" gutterBottom>
                  Environmental Indicators
                </Typography>
                {[
                  { icon: <WaterDropIcon fontSize="small" />, label: 'Rainfall (14-day avg)', value: '25 mm', bar: 60, color: '#60a5fa' },
                  { icon: <ThermostatIcon fontSize="small" />, label: 'Temperature', value: '28.5°C', bar: 75, color: '#f97316' },
                  { icon: <BugReportIcon fontSize="small" />, label: 'Cases (7-day lag)', value: '18', bar: 45, color: '#a78bfa' },
                ].map((item, i) => (
                  <Box key={i} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                        {item.icon}
                        <Typography variant="body2">{item.label}</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight={700}>{item.value}</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={item.bar}
                      sx={{
                        borderRadius: 2, height: 6,
                        bgcolor: 'rgba(255,255,255,0.06)',
                        '& .MuiLinearProgress-bar': { bgcolor: item.color, borderRadius: 2 }
                      }}
                    />
                  </Box>
                ))}
              </Paper>
            </Grid>

            {/* Causal Insights */}
            <Grid size={{ xs: 12, md: 4 }}>
              <Paper sx={{
                p: 4, borderRadius: 4, height: '100%',
                border: '1px solid', borderColor: 'divider',
                background: 'rgba(255,255,255,0.03)'
              }}>
                <Typography variant="overline" color="text.secondary" fontWeight={700} display="block" gutterBottom>
                  Why Is Risk {data.risk_score > 50 ? 'Elevated' : 'Low'}?
                </Typography>
                <List disablePadding>
                  {data.insights.map((insight, i) => (
                    <ListItem key={i} disablePadding sx={{ mb: 2, alignItems: 'flex-start' }}>
                      <ListItemIcon sx={{ minWidth: 32, mt: 0.5 }}>
                        <WarningAmberIcon fontSize="small" sx={{ color: '#f97316' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={insight}
                        primaryTypographyProps={{ variant: 'body2', color: 'text.secondary', lineHeight: 1.6 }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>

            {/* Public Health Actions */}
            <Grid size={{ xs: 12 }}>
              <Paper sx={{
                p: 4, borderRadius: 4,
                border: '1px solid', borderColor: 'divider',
                background: 'linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(59,130,246,0.05) 100%)'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
                  <ShieldIcon sx={{ color: 'primary.main' }} />
                  <Typography variant="h6" fontWeight={700}>
                    Recommended Public Health Actions
                  </Typography>
                </Box>
                <Grid container spacing={2}>
                  {[
                    { title: 'Eliminate Standing Water', desc: 'Check and empty containers, flower pots, and coolers weekly.' },
                    { title: 'Use Mosquito Repellent', desc: 'Apply DEET-based repellents during dawn and dusk peak hours.' },
                    { title: 'Monitor Symptoms', desc: 'Seek care immediately for sudden high fever, severe headache, or joint pain.' },
                    { title: 'Community Reporting', desc: 'Report suspected cases to BBMP health authorities for rapid surveillance.' },
                  ].map((action, i) => (
                    <Grid size={{ xs: 12, sm: 6 }} key={i}>
                      <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
                        <InfoOutlinedIcon fontSize="small" sx={{ color: 'primary.main', mt: 0.2, flexShrink: 0 }} />
                        <Box>
                          <Typography variant="body2" fontWeight={700} gutterBottom>{action.title}</Typography>
                          <Typography variant="body2" color="text.secondary">{action.desc}</Typography>
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>

          </Grid>
        </Fade>
      )}
    </Container>
  );
}
