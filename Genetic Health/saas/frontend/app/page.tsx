import Link from 'next/link';
import Navbar from '@/components/Navbar';

const features = [
  {
    icon: '🔬',
    iconClass: 'purple',
    title: 'Disease Risk Analysis',
    desc: 'ClinVar-backed pathogenic variant detection across thousands of conditions — from APOE4 to rare carrier statuses.',
  },
  {
    icon: '💊',
    iconClass: 'amber',
    title: 'Drug Interactions',
    desc: 'PharmGKB-powered pharmacogenomics. Know how your genes affect drug metabolism before the prescription.',
  },
  {
    icon: '🧬',
    iconClass: 'green',
    title: 'Full Genetic Profile',
    desc: 'Methylation, cardiovascular, sleep, fitness, nutrition — 200+ curated SNPs interpreted with impact magnitude.',
  },
  {
    icon: '📋',
    iconClass: 'blue',
    title: 'Actionable Protocols',
    desc: 'Personalized daily health stacks, dietary frameworks, exercise programs, and monitoring schedules.',
  },
];

import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function LandingPage() {
  const { userId } = await auth();
  if (userId) {
    redirect('/dashboard');
  }

  return (
    <>
      <Navbar />

      <main>
        {/* Hero */}
        <section className="hero">
          <div className="hero-eyebrow">
            <span>🧬</span>
            <span>Powered by ClinVar & PharmGKB</span>
          </div>

          <h1 className="hero-title">
            <span className="gradient-text">Your Genome.</span>
            <br />
            Your Health Intelligence.
          </h1>

          <p className="hero-subtitle">
            Upload your 23andMe raw data and get a comprehensive, clinically-informed
            report on disease risks, drug interactions, and personalized health protocols.
          </p>

          <div className="hero-cta">
            <Link href="/sign-up" className="btn btn-primary btn-lg">
              Start Free Analysis →
            </Link>
            <Link href="/sign-in" className="btn btn-ghost btn-lg">
              Sign In
            </Link>
          </div>
        </section>

        {/* Features */}
        <section style={{ padding: '0 24px 100px' }}>
          <div className="container">
            <div style={{ textAlign: 'center', marginBottom: 48 }}>
              <h2>Everything you need to understand your DNA</h2>
              <p style={{ marginTop: 12 }}>
                Not a gimmick. Real genetic databases. Real interpretations.
              </p>
            </div>
            <div className="features-grid">
              {features.map((f) => (
                <div key={f.title} className="feature-card">
                  <div className={`feature-icon ${f.iconClass}`}>{f.icon}</div>
                  <h3>{f.title}</h3>
                  <p>{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How it works */}
        <section style={{ padding: '60px 24px 100px', borderTop: '1px solid var(--border)' }}>
          <div className="container" style={{ maxWidth: 720, textAlign: 'center' }}>
            <h2>Three steps to full clarity</h2>
            <p style={{ marginTop: 12, marginBottom: 48 }}>
              From raw genome file to actionable health protocol in minutes.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
              {[
                { step: '01', title: 'Upload', desc: 'Paste or upload your 23andMe .txt file or an existing Markdown report.' },
                { step: '02', title: 'Store', desc: 'Your report is saved securely. Only you can access it — guaranteed by Row Level Security.' },
                { step: '03', title: 'Review', desc: 'Read your beautifully rendered genetic report from any device, any time.' },
              ].map((s) => (
                <div key={s.step} className="glass-card" style={{ padding: '28px 20px' }}>
                  <div style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: 'var(--accent)',
                    letterSpacing: '0.1em',
                    marginBottom: 12
                  }}>
                    STEP {s.step}
                  </div>
                  <h3 style={{ marginBottom: 8 }}>{s.title}</h3>
                  <p style={{ fontSize: '0.88rem' }}>{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Banner */}
        <section style={{
          padding: '80px 24px',
          background: 'linear-gradient(135deg, rgba(124,111,247,0.08) 0%, rgba(168,85,247,0.06) 100%)',
          borderTop: '1px solid rgba(124,111,247,0.15)'
        }}>
          <div className="container" style={{ textAlign: 'center' }}>
            <h2>Ready to understand your genetics?</h2>
            <p style={{ marginTop: 12, marginBottom: 32 }}>
              Free to start. Secure by design. Your data, your reports.
            </p>
            <Link href="/sign-up" className="btn btn-primary btn-lg">
              Create Free Account →
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer style={{
          borderTop: '1px solid var(--border)',
          padding: '32px 24px',
          textAlign: 'center',
          color: 'var(--text-muted)',
          fontSize: '0.82rem'
        }}>
          <div className="container">
            <p>GENOME is for informational purposes only. Not a substitute for clinical diagnosis.</p>
            <p style={{ marginTop: 8 }}>© {new Date().getFullYear()} GENOME Health Intelligence</p>
          </div>
        </footer>
      </main>
    </>
  );
}
