/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,ts,tsx,js,jsx}'
  ],
  theme: {
    extend: {
      typography: () => ({
        notion: {
          css: {
            '--tw-prose-body': 'var(--text-primary)',
            '--tw-prose-headings': 'var(--text-primary)',
            '--tw-prose-links': 'var(--primary)',
            '--tw-prose-bullets': 'var(--text-secondary)',
            '--tw-prose-hr': 'color-mix(in oklch, var(--glass-border) 80%, transparent)',
            'h1, h2, h3': {
              fontWeight: '700',
              lineHeight: '1.25'
            },
            h1: { fontSize: '28px', marginTop: '1.2em', marginBottom: '.6em' },
            h2: { fontSize: '22px', marginTop: '1.1em', marginBottom: '.5em' },
            h3: { fontSize: '18px', marginTop: '1em', marginBottom: '.4em' },
            blockquote: {
              margin: '.8em 0',
              padding: '.6em .9em',
              borderLeft: '3px solid color-mix(in oklch, var(--primary) 40%, white)',
              background: 'color-mix(in oklch, var(--glass-bg) 88%, transparent)',
              borderRadius: '8px'
            },
            hr: { border: 'none', height: '1px', background: 'color-mix(in oklch, var(--glass-border) 80%, transparent)', margin: '1.2em 0' },
            ul: { listStyle: 'disc outside', paddingLeft: '1.5rem', margin: '.5em 0' },
            ol: { listStyle: 'decimal outside', paddingLeft: '1.5rem', margin: '.5em 0' },
            li: { margin: '.25em 0' },
            img: { borderRadius: '0.5rem', boxShadow: '0 4px 18px rgba(0,0,0,.25)' },
            code: { background: 'color-mix(in oklch, var(--glass-bg) 88%, transparent)', borderRadius: '6px', padding: '0.15em 0.35em' },
            pre: { background: 'color-mix(in oklch, var(--glass-bg) 92%, transparent)', borderRadius: '8px', padding: '.9rem 1rem' }
          }
        }
      })
    }
  },
  plugins: [
    require('@tailwindcss/typography')
  ]
}

