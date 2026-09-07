import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Finding {
  detector: string
  score: number
  confidence: number
  finding_text: string
  evidence_refs: string[]
  blocked_reason?: string
}

interface DetectorResponse {
  detector: string
  name: string
  findings_count: number
  findings: Finding[]
}

// Beautiful color palette inspired by Nordic/Singapore government design
const COLORS = {
  primary: '#2563EB',      // Royal blue
  secondary: '#10B981',    // Emerald green
  accent: '#F59E0B',       // Amber gold
  danger: '#EF4444',       // Red
  bgGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  cardBg: 'rgba(255, 255, 255, 0.95)',
  textDark: '#1F2937',
  textLight: '#6B7280',
}

function App() {
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [testType, setTestType] = useState<'d1-flagged' | 'd1-clean' | 'case-analysis'>('d1-flagged')

  interface TestCase {
    gstin: string
    amount: string
    description: string
    invoice_lines: Array<{ taxable_value: number; quantity_kg: number; hsn: string }>
  }

  const testCases: Record<string, TestCase> = {
    'd1-flagged': {
      gstin: "P2OVER0001",
      amount: "₹23.94 Crore",
      description: "Over-invoiced synthetic fabric at 21× market price",
      invoice_lines: [{ taxable_value: 2394000, quantity_kg: 760, hsn: "540792" }]
    },
    'd1-clean': {
      gstin: "CLEAN0042",
      amount: "₹2.80 Lakh",
      description: "Normal cotton fabric at market price (Hard Negative N1)",
      invoice_lines: [{ taxable_value: 280000, quantity_kg: 1000, hsn: "520831" }]
    },
    'case-analysis': {
      gstin: "P2OVER0001",
      amount: "₹12.00 Crore",
      description: "Full case analysis - Merchant exporter with shell suppliers",
      invoice_lines: [{ taxable_value: 2394000, quantity_kg: 760, hsn: "540792" }]
    }
  }

  async function runAnalysis() {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const testCase = testCases[testType]
      
      if (testType === 'd1-flagged' || testType === 'd1-clean') {
        const response = await axios.post<DetectorResponse>(
          `${API_URL}/api/detectors/d1`,
          testCase.invoice_lines,
          { headers: { 'Content-Type': 'application/json' } }
        )
        
        setResult(JSON.stringify(response.data, null, 2))
      } else {
        const response = await axios.post<any>(
          `${API_URL}/api/cases/analyze`,
          {
            gstin: testCase.gstin,
            claim_id: `RC-${testCase.gstin}`,
            invoice_lines: testCase.invoice_lines
          },
          { headers: { 'Content-Type': 'application/json' } }
        )
        
        setResult(JSON.stringify(response.data, null, 2))
      }
    } catch (err: any) {
      setError(`Error: ${err.response?.data?.detail || err.message}`)
    } finally {
      setTimeout(() => setLoading(false), 1000)
    }
  }

  // Auto-run on mount for demo effect
  useEffect(() => {
    runAnalysis()
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      background: COLORS.bgGradient,
      backgroundImage: `
        radial-gradient(at 0% 0%, rgba(37, 99, 235, 0.1) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(118, 75, 162, 0.1) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.1) 0px, transparent 50%),
        radial-gradient(at 0% 100%, rgba(245, 158, 11, 0.1) 0px, transparent 50%)
      `,
      padding: '2rem'
    }}>
      {/* Floating Glass Cards */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'grid',
        gap: '2rem',
        gridTemplateColumns: '1fr 400px'
      }}>
        {/* Left Column - Main Content */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Hero Header */}
          <div style={{
            backgroundColor: COLORS.cardBg,
            borderRadius: '24px',
            padding: '3rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '1.5rem' }}>
              <div style={{
                width: '80px',
                height: '80px',
                background: 'linear-gradient(135deg, #2563EB, #10B981)',
                borderRadius: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '3rem'
              }}>🔍</div>
              <div>
                <h1 style={{
                  fontSize: '2.5rem',
                  fontWeight: '800',
                  background: 'linear-gradient(135deg, #1F2937, #6B7280)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  margin: 0,
                  letterSpacing: '-0.02em'
                }}>PACE Platform</h1>
                <p style={{ color: COLORS.textLight, fontSize: '1.1rem', margin: '0.5rem 0 0 0' }}>
                  Physical Plausibility Engine for GST Adjudication
                </p>
              </div>
            </div>

            {/* Statistics Cards */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1.5rem',
              marginTop: '3rem'
            }}>
              {[
                { label: 'Detectors Active', value: '1/4', icon: '⚡', color: COLORS.primary },
                { label: 'Threshold Stage', value: 'S1-S2', icon: '📊', color: COLORS.accent },
                { label: 'Data Maturity', value: 'Synthetic', icon: '🧪', color: COLORS.secondary },
                { label: 'Fairness Controls', value: '✓ Enabled', icon: '🛡️', color: COLORS.secondary }
              ].map((stat, i) => (
                <div key={i} style={{
                  backgroundColor: 'white',
                  borderRadius: '16px',
                  padding: '1.5rem',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  cursor: 'pointer',
                  hover: { transform: 'translateY(-4px)', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)'
                  e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                >
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{stat.icon}</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: stat.color }}>{stat.value}</div>
                  <div style={{ fontSize: '0.875rem', color: COLORS.textLight }}>{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* System Overview */}
          <div style={{
            backgroundColor: COLORS.cardBg,
            borderRadius: '24px',
            padding: '2.5rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <h2 style={{ 
              fontSize: '1.5rem', 
              fontWeight: '700',
              color: COLORS.textDark,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}>
              <span style={{ fontSize: '1.75rem' }}>📋</span> System Overview
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '2rem',
              marginTop: '1.5rem'
            }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: COLORS.textDark, marginBottom: '1rem' }}>
                  Current Capabilities
                </h3>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  spaceyBetween: '0.75rem'
                }}>
                  {[
                    '✅ D1 Price Closure Detector (Live)',
                    '⏳ D2 Capacity Closure (Coming Soon)',
                    '⏳ D3 Premises Aggregation (Coming Soon)',
                    '⏳ D4 Network Topology (Coming Soon)'
                  ].map((item, i) => (
                    <li key={i} style={{
                      padding: '0.75rem 1rem',
                      backgroundColor: 'white',
                      borderRadius: '12px',
                      marginBottom: '0.5rem',
                      fontSize: '0.95rem',
                      fontWeight: '500',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}>{item}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: COLORS.textDark, marginBottom: '1rem' }}>
                  Demo Cases Ready
                </h3>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  spaceyBetween: '0.75rem'
                }}>
                  {[
                    '🎯 P2 Pattern: Over-invoicing (21×)',
                    '🛡️ Hard Negative N1: Clean Trader',
                    '🔴 Red Tier: Flagged Case Analysis',
                    '🟢 Green Tier: Normal Business'
                  ].map((item, i) => (
                    <li key={i} style={{
                      padding: '0.75rem 1rem',
                      backgroundColor: 'white',
                      borderRadius: '12px',
                      marginBottom: '0.5rem',
                      fontSize: '0.95rem',
                      fontWeight: '500',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* API Response Display */}
          {error && (
            <div style={{
              backgroundColor: '#EF4444',
              color: 'white',
              borderRadius: '16px',
              padding: '1.5rem',
              boxShadow: '0 10px 25px rgba(239, 68, 68, 0.3)'
            }}>
              <strong>⚠️ Error:</strong> {error}
            </div>
          )}

          {result && (
            <div style={{
              backgroundColor: COLORS.cardBg,
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              fontFamily: '"SF Mono", "Fira Code", monospace',
              fontSize: '0.875rem',
              lineHeight: '1.6'
            }}>
              <h3 style={{ 
                fontSize: '1.1rem', 
                fontWeight: '600',
                color: COLORS.textDark,
                marginBottom: '1rem',
                borderBottom: '2px solid #E5E7EB',
                paddingBottom: '0.75rem'
              }}>📊 Detection Results</h3>
              <pre style={{ 
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                color: '#1F2937'
              }}>{result}</pre>
            </div>
          )}
        </div>

        {/* Right Column - Control Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Test Selector Card */}
          <div style={{
            backgroundColor: COLORS.cardBg,
            borderRadius: '24px',
            padding: '2rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            backdropFilter: 'blur(20px)'
          }}>
            <h2 style={{ 
              fontSize: '1.25rem', 
              fontWeight: '700',
              color: COLORS.textDark,
              marginBottom: '1.5rem'
            }}>🧪 Test Selector</h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { id: 'd1-flagged', label: 'Flagged Invoice (P2)', desc: '21× price multiple' },
                { id: 'd1-clean', label: 'Clean Invoice (N1)', desc: 'Normal pricing' },
                { id: 'case-analysis', label: 'Full Case Analysis', desc: 'Complete workflow' }
              ].map((test) => (
                <button
                  key={test.id}
                  onClick={() => {
                    setTestType(test.id as any)
                    runAnalysis()
                  }}
                  disabled={loading}
                  style={{
                    padding: '1.25rem',
                    borderRadius: '16px',
                    border: 'none',
                    background: testType === test.id 
                      ? 'linear-gradient(135deg, #2563EB, #10B981)'
                      : 'linear-gradient(135deg, #f3f4f6, #e5e7eb)',
                    color: testType === test.id ? 'white' : '#374151',
                    fontWeight: '600',
                    fontSize: '0.95rem',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading && testType !== test.id ? 0.6 : 1,
                    transition: 'all 0.3s ease',
                    boxShadow: testType === test.id 
                      ? '0 10px 25px rgba(37, 99, 235, 0.3)' 
                      : '0 2px 8px rgba(0,0,0,0.1)',
                    textAlign: 'left',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.currentTarget.style.transform = 'translateX(8px)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateX(0)'
                  }}
                >
                  <div style={{ fontSize: '1.1rem', fontWeight: '700' }}>{test.label}</div>
                  <div style={{ 
                    fontSize: '0.8rem', 
                    opacity: 0.8,
                    marginTop: '0.25rem'
                  }}>{test.desc}</div>
                </button>
              ))}
            </div>

            {/* Run Button */}
            <button
              onClick={runAnalysis}
              disabled={loading}
              style={{
                width: '100%',
                padding: '1.25rem',
                marginTop: '1.5rem',
                borderRadius: '16px',
                border: 'none',
                background: 'linear-gradient(135deg, #10B981, #059669)',
                color: 'white',
                fontWeight: '700',
                fontSize: '1.1rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1,
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 25px rgba(16, 185, 129, 0.3)'
              }}
            >
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
                  <span style={{ 
                    width: '24px', 
                    height: '24px', 
                    border: '3px solid white', 
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}></span>
                  Running Analysis...
                </span>
              ) : (
                '▶️ Run Analysis'
              )}
            </button>

            {/* Live Status Indicator */}
            <div style={{
              marginTop: '1.5rem',
              padding: '1rem',
              backgroundColor: '#ECFDF5',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}>
              <div style={{
                width: '12px',
                height: '12px',
                backgroundColor: '#10B981',
                borderRadius: '50%',
                animation: 'pulse 2s infinite'
              }}></div>
              <div style={{ fontSize: '0.875rem', color: '#065F46', fontWeight: '500' }}>
                System Operational • API Connected
              </div>
            </div>
          </div>

          {/* Info Card */}
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '24px',
            padding: '1.5rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <h3 style={{ 
              fontSize: '1rem', 
              fontWeight: '600',
              color: COLORS.textDark,
              marginBottom: '0.75rem'
            }}>ℹ️ How to Use</h3>
            <ol style={{
              paddingLeft: '1.25rem',
              color: COLORS.textLight,
              lineHeight: '1.8',
              fontSize: '0.875rem'
            }}>
              <li>Select test case above</li>
              <li>Click "Run Analysis"</li>
              <li>View detection results</li>
              <li>Check fraud patterns detected</li>
              <li>Review fairness controls</li>
            </ol>
          </div>

        </div>
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: '1400px',
        margin: '4rem auto 0',
        padding: '2rem',
        textAlign: 'center',
        color: 'rgba(255, 255, 255, 0.8)'
      }}>
        <p style={{ fontSize: '0.875rem' }}>
          PACE Prototype v1.0 • Built for SIH 2026 • Based on workflow.md specification
        </p>
      </div>

      {/* Global Styles for Animations */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  )
}

export default App
