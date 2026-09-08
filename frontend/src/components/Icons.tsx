import React from 'react'

type IconProps = React.SVGProps<SVGSVGElement> & { size?: number }

const base = (size: number, props: React.SVGProps<SVGSVGElement>) => ({
  width: size,
  height: size,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
  ...props,
})

export function RadarIcon({ size = 22, ...props }: IconProps) {
  return <svg {...base(size, props)}><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/><path d="M12 12 18.4 7.8"/><path d="M12 3v2M3 12h2M19 12h2M12 19v2"/></svg>
}

export function SparkIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M12 2.7c.7 4.8 2.8 6.9 7.5 7.5-4.7.7-6.8 2.8-7.5 7.5-.7-4.7-2.8-6.8-7.5-7.5C9.2 9.6 11.3 7.5 12 2.7Z"/><path d="M19.1 15.9c.2 1.8 1 2.6 2.8 2.8-1.8.2-2.6 1-2.8 2.8-.2-1.8-1-2.6-2.8-2.8 1.8-.2 2.6-1 2.8-2.8Z"/></svg>
}

export function ShieldIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M12 3 5.5 5.7v5.2c0 4.4 2.6 7.8 6.5 10.1 3.9-2.3 6.5-5.7 6.5-10.1V5.7L12 3Z"/><path d="m9.1 12.1 1.9 1.9 4-4.2"/></svg>
}

export function ArrowIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M5 12h13"/><path d="m14 7 5 5-5 5"/></svg>
}

export function PlayIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="m8 5 11 7-11 7V5Z" fill="currentColor" stroke="none"/></svg>
}

export function BuildingIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M4 21V5.5L12 2v19"/><path d="M12 8h8v13"/><path d="M2 21h20"/><path d="M7 8h1M7 12h1M7 16h1M15 12h1M15 16h1"/></svg>
}

export function NetworkIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><circle cx="6" cy="6" r="2.2"/><circle cx="18" cy="7" r="2.2"/><circle cx="8" cy="18" r="2.2"/><circle cx="18" cy="18" r="2.2"/><path d="m8 6.3 7.8.5M7 8l.5 7.8M10 17.9l5.8.1M16.8 9l.4 6.8M8 7.7l8 8.7"/></svg>
}

export function PriceIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M4 6h16M6 3v6M18 3v6"/><path d="M5 11h14v9H5z"/><path d="M8 15h8M12 12.5v5"/></svg>
}

export function MapPinIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M20 10c0 5.2-8 11-8 11S4 15.2 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>
}

export function GraphIcon({ size = 20, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/><path d="m4 8 6-4 6 6 4-4"/></svg>
}

export function CheckIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="m5 12.5 4.2 4.2L19 7"/></svg>
}

export function AlertIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v4.5M12 17h.01"/></svg>
}

export function LockIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><rect x="4" y="10" width="16" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>
}

export function SearchIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><circle cx="10.8" cy="10.8" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>
}

export function ChevronIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="m8 10 4 4 4-4"/></svg>
}

export function CopyIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><rect x="8" y="8" width="11" height="11" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/></svg>
}

export function ExternalIcon({ size = 16, ...props }: IconProps) {
  return <svg {...base(size, props)}><path d="M14 4h6v6M20 4l-9 9"/><path d="M20 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h5"/></svg>
}

export function ClockIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
}

export function DatabaseIcon({ size = 18, ...props }: IconProps) {
  return <svg {...base(size, props)}><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>
}
