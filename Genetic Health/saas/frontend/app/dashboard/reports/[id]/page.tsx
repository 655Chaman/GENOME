import { auth } from '@clerk/nextjs/server';
import { redirect, notFound } from 'next/navigation';
import Link from 'next/link';
import { supabaseAdmin } from '@/lib/supabase';
import MarkdownViewer from '@/components/MarkdownViewer';
import type { Metadata } from 'next';
import { Box, Typography, Paper, Button, Chip } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

interface Props {
  params: Promise<{ id: string }>;
}

const TYPE_META: Record<string, { label: string; color: "error" | "secondary" | "success" | "primary" | "default"; icon: string }> = {
  disease_risk: { label: 'Disease Risk Report', color: 'error', icon: '🧬' },
  genetic:      { label: 'Genetic Profile',     color: 'secondary', icon: '🔬' },
  protocol:     { label: 'Health Protocol',     color: 'success', icon: '📋' },
  custom:       { label: 'Report',              color: 'primary', icon: '📄' },
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const { data } = await supabaseAdmin.from('reports').select('title').eq('id', id).single();
  return { title: data?.title ? `${data.title} — GENOME` : 'Report — GENOME' };
}

export default async function ReportPage({ params }: Props) {
  const { userId } = await auth();
  if (!userId) redirect('/sign-in');

  const { id } = await params;

  const { data: report, error } = await supabaseAdmin
    .from('reports')
    .select('*')
    .eq('id', id)
    .eq('user_id', userId)
    .single();

  if (error || !report) notFound();

  const meta = TYPE_META[report.report_type] ?? TYPE_META.custom;
  const date = new Date(report.created_at).toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });

  return (
    <Box sx={{ maxWidth: 860, mx: 'auto', p: { xs: 2, md: 4 } }}>
      <Box sx={{ mb: 4 }}>
        <Link href="/dashboard" style={{ textDecoration: 'none' }}>
          <Button 
            startIcon={<ArrowBackIcon />}
            sx={{ color: 'text.secondary', textTransform: 'none' }}
          >
            Back to Dashboard
          </Button>
        </Link>
      </Box>

      <Paper 
        sx={{ 
          p: { xs: 3, md: 5 }, 
          mb: 4, 
          borderRadius: 3, 
          border: '1px solid', 
          borderColor: 'divider',
          background: 'linear-gradient(180deg, rgba(99,102,241,0.08) 0%, transparent 100%)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Typography variant="h3">{meta.icon}</Typography>
          <Chip label={meta.label} color={meta.color} />
        </Box>
        
        <Typography variant="h3" component="h1" fontWeight={700} gutterBottom>
          {report.title}
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          Generated on {date}
        </Typography>
      </Paper>

      <Paper sx={{ p: { xs: 3, md: 5 }, borderRadius: 3 }}>
        <MarkdownViewer content={report.content} />
      </Paper>

      <Box sx={{ mt: 6, display: 'flex', justifyContent: 'center' }}>
        <Link href="/dashboard" style={{ textDecoration: 'none' }}>
          <Button 
            variant="contained" 
            size="large"
            startIcon={<ArrowBackIcon />}
            sx={{ textTransform: 'none', borderRadius: 2 }}
          >
            Back to Dashboard
          </Button>
        </Link>
      </Box>
    </Box>
  );
}
