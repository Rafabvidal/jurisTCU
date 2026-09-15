import { vi } from 'vitest'

vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000/api')

// vue3-apexcharts depende de window APIs que jsdom não implementa; mockamos como stub.
vi.mock('vue3-apexcharts', () => ({
  default: {
    name: 'ApexchartStub',
    props: ['type', 'series', 'options', 'height', 'width'],
    template: '<div data-test="apexchart-stub"><slot /></div>',
  },
}))

if (!('matchMedia' in window)) {
  Object.defineProperty(window, 'matchMedia', {
    value: () => ({
      matches: false,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }),
  })
}
