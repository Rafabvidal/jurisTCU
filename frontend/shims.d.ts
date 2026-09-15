declare module 'eslint-plugin-oxlint' {
  const pluginOxlint: {
    buildFromOxlintConfigFile: (configFilePath: string) => unknown[]
  }

  export default pluginOxlint
}

declare module 'vue3-apexcharts' {
  import type { DefineComponent } from 'vue'

  const VueApexCharts: DefineComponent<{
    type?: string
    series?: unknown
    options?: Record<string, unknown>
    width?: string | number
    height?: string | number
  }>

  export default VueApexCharts
}
