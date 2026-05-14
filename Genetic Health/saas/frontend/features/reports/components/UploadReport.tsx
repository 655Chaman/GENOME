'use client';

import React, { useState, useRef } from 'react';
import { useUser } from '@clerk/nextjs';
import { 
  Box, Button, Typography, Paper, TextField, LinearProgress, IconButton
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

interface Props {
  onSaved: () => void;
}

export const UploadReport: React.FC<Props> = ({ onSaved }) => {
  const { user } = useUser();
  const [open, setOpen] = useState(false);
  const [subjectName, setSubjectName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith('.txt')) {
      setFile(f);
      if (!subjectName) setSubjectName(user?.firstName || 'My Patient');
    } else {
      alert('Please upload a .txt 23andMe file');
    }
  };

  const handleProcess = async () => {
    if (!file || !subjectName.trim() || !user) {
      alert('File and Subject Name are required');
      return;
    }
    
    setLoading(true);
    setProgress(0);
    
    const progressInterval = setInterval(() => {
      setProgress(p => (p >= 95 ? 95 : p + Math.floor(Math.random() * 10) + 2));
    }, 500);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', user.id);
      formData.append('subject_name', subjectName.trim());

      const res = await fetch('http://localhost:8001/api/process', {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) throw new Error('Failed to process genome');
      
      setProgress(100);
      clearInterval(progressInterval);
      
      setTimeout(() => {
        setFile(null);
        setSubjectName('');
        setOpen(false);
        setLoading(false);
        onSaved();
      }, 1000);
      
    } catch (err) {
      clearInterval(progressInterval);
      setLoading(false);
      alert(err instanceof Error ? err.message : 'Failed to process');
    }
  };

  if (!open) {
    return (
      <Button 
        variant="contained" 
        startIcon={<AutoAwesomeIcon />}
        onClick={() => setOpen(true)}
        sx={{ mb: 4, textTransform: 'none', borderRadius: 2 }}
      >
        Analyze New Genome
      </Button>
    );
  }

  return (
    <Paper sx={{ p: 4, mb: 4, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <UploadFileIcon color="primary" /> Analyze New Genome
        </Typography>
        <IconButton onClick={() => setOpen(false)} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      <TextField
        fullWidth
        label="Subject Name"
        variant="outlined"
        size="small"
        placeholder="e.g. Jane Doe"
        value={subjectName}
        onChange={(e) => setSubjectName(e.target.value)}
        sx={{ mb: 3 }}
      />

      <Box
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        sx={{
          border: '2px dashed',
          borderColor: 'divider',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          mb: 3,
          bgcolor: 'background.default',
          '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
        }}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".txt"
          style={{ display: 'none' }}
          onChange={(e) => { 
            const f = e.target.files?.[0]; 
            if (f && f.name.endsWith('.txt')) {
              setFile(f);
              if (!subjectName) setSubjectName(user?.firstName || 'My Patient');
            } else if (f) {
              alert('Please upload a .txt 23andMe file');
            }
          }}
        />
        <UploadFileIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
        <Typography variant="body1" fontWeight={500}>
          Drop your 23andMe .txt file here or click to browse
        </Typography>
        {file && (
          <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
            ✓ Selected: {file.name}
          </Typography>
        )}
      </Box>

      {loading ? (
        <Box sx={{ width: '100%' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">Analyzing Genome Data...</Typography>
            <Typography variant="body2" color="text.secondary">{progress}%</Typography>
          </Box>
          <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
        </Box>
      ) : (
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            onClick={handleProcess} 
            disabled={!file || !subjectName}
            startIcon={<AutoAwesomeIcon />}
            sx={{ textTransform: 'none' }}
          >
            Process Genome
          </Button>
          <Button variant="outlined" onClick={() => setOpen(false)} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
        </Box>
      )}
    </Paper>
  );
};
