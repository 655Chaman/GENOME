import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Button, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ScienceIcon from '@mui/icons-material/Science';
import SpaIcon from '@mui/icons-material/Spa';
import FavoriteIcon from '@mui/icons-material/Favorite';
import ArticleIcon from '@mui/icons-material/Article';
import type { Report } from '~features/reports/types/report';

interface Props {
  report: Report;
  onDelete: (id: string) => void;
}

const TYPE_META: Record<string, { label: string; color: "error" | "secondary" | "success" | "primary" | "default"; icon: React.ReactElement }> = {
  disease_risk: { label: 'Disease Risk',    color: 'error',     icon: <FavoriteIcon fontSize="small" /> },
  genetic:      { label: 'Genetic Profile', color: 'secondary', icon: <ScienceIcon fontSize="small" /> },
  protocol:     { label: 'Health Protocol', color: 'success',   icon: <SpaIcon fontSize="small" /> },
  custom:       { label: 'Custom',          color: 'primary',   icon: <ArticleIcon fontSize="small" /> },
};

export const ReportCard: React.FC<Props> = ({ report, onDelete }) => {
  const meta = TYPE_META[report.report_type] ?? TYPE_META.custom;
  const date = new Date(report.created_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Delete "${report.title}"? This cannot be undone.`)) {
      onDelete(report.id);
    }
  };

  const handleNavigation = () => {
    window.location.href = `/dashboard/reports/${report.id}`;
  };

  return (
    <Card 
      onClick={handleNavigation}
      sx={{ 
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}
    >
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ color: `${meta.color}.main`, display: 'flex', alignItems: 'center' }}>
              {meta.icon}
            </Box>
            <Chip size="small" label={meta.label} color={meta.color} variant="outlined" />
          </Box>
        </Box>
        
        <Typography variant="h6" component="div" sx={{ fontWeight: 600, lineHeight: 1.3 }}>
          {report.title}
        </Typography>

        <Typography variant="body2" color="text.secondary">
          🗓 {date}
        </Typography>

        <Box sx={{ mt: 'auto', pt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid', borderColor: 'divider' }}>
          <Button size="small" endIcon={<ArrowForwardIcon />} sx={{ textTransform: 'none' }}>
            View Report
          </Button>
          <IconButton size="small" color="error" onClick={handleDelete} aria-label="delete">
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
};
