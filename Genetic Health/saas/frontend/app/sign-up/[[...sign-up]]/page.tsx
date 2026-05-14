import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg-base)',
      padding: '24px',
    }}>
      <div style={{ marginBottom: 32, textAlign: 'center' }}>
        <div style={{
          fontSize: '2rem',
          marginBottom: 8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
        }}>
          <span style={{
            width: 40,
            height: 40,
            background: 'linear-gradient(135deg, var(--accent), #a855f7)',
            borderRadius: 10,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
          }}>🧬</span>
          <span style={{ fontWeight: 800, fontSize: '1.3rem', color: 'var(--text-primary)' }}>GENOME</span>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Create your free account</p>
      </div>
      <SignUp routing="path" path="/sign-up" fallbackRedirectUrl="/dashboard" forceRedirectUrl="/dashboard" />
    </div>
  );
}
