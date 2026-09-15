<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

import {
  CHART_FONT_FAMILY,
  CHART_HEIGHT,
} from '@/shared/constants/charts'

export type BaseChartType =
  | 'donut'
  | 'pie'
  | 'bar'
  | 'radialBar'
  | 'line'
  | 'area'

interface Props {
  type: BaseChartType
  series: number[] | { name: string; data: number[] }[]
  labels?: string[]
  colors?: string[]
  height?: number
  horizontal?: boolean
  valueFormatter?: (value: number) => string
  centerLabel?: string
  centerValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  labels: () => [],
  colors: () => [],
  height: undefined,
  horizontal: true,
  valueFormatter: undefined,
  centerLabel: undefined,
  centerValue: undefined,
})

function resolveHeight(): number {
  if (props.height) return props.height
  if (props.type === 'donut' || props.type === 'pie') return CHART_HEIGHT.donut
  if (props.type === 'radialBar') return CHART_HEIGHT.radial
  return CHART_HEIGHT.bar
}

const chartOptions = computed<Record<string, unknown>>(() => {
  const tooltipOptions: Record<string, unknown> = {
    theme: 'light',
  }

  if (props.valueFormatter) {
    tooltipOptions.y = { formatter: props.valueFormatter }
  }

  const baseOptions: Record<string, unknown> = {
    chart: {
      type: props.type,
      fontFamily: CHART_FONT_FAMILY,
      toolbar: { show: false },
      animations: { enabled: true, speed: 320 },
      foreColor: '#314567',
    },
    colors: props.colors.length ? props.colors : undefined,
    labels: props.labels,
    legend: {
      position: 'bottom',
      fontSize: '12px',
      fontWeight: 500,
      markers: { size: 6 },
      itemMargin: { horizontal: 8, vertical: 4 },
    },
    dataLabels: {
      enabled: props.type === 'donut' || props.type === 'pie' || props.type === 'radialBar',
      style: { fontSize: '11px', fontWeight: 600 },
    },
    tooltip: tooltipOptions,
  }

  if (props.type !== 'radialBar') {
    baseOptions.grid = {
      borderColor: '#e5ebf5',
      strokeDashArray: 4,
    }
  }

  if (props.type === 'bar') {
    baseOptions.plotOptions = {
      bar: {
        horizontal: props.horizontal,
        borderRadius: 6,
        columnWidth: '60%',
        distributed: true,
      },
    }
    baseOptions.xaxis = {
      categories: props.labels,
      labels: { style: { fontSize: '11px' } },
    }
    baseOptions.legend = { show: false }
  }

  if (props.type === 'donut' || props.type === 'pie') {
    baseOptions.plotOptions = {
      pie: {
        donut: {
          size: '64%',
          labels: {
            show: true,
            name: { fontSize: '12px', color: '#5d708f' },
            value: {
              fontSize: '20px',
              fontWeight: 700,
              color: '#0f2d57',
            },
            total: {
              show: true,
              label: 'Total',
              fontSize: '12px',
              color: '#5d708f',
              fontWeight: 500,
            },
          },
        },
      },
    }
  }

  if (props.type === 'radialBar') {
    baseOptions.plotOptions = {
      radialBar: {
        startAngle: -135,
        endAngle: 135,
        hollow: { size: '58%' },
        track: {
          background: '#dbe7ff',
          strokeWidth: '100%',
          margin: 0,
        },
        stroke: {
          lineCap: 'round',
        },
        dataLabels: {
          name: {
            show: true,
            fontSize: '12px',
            color: '#5d708f',
            offsetY: -4,
          },
          value: {
            show: true,
            fontSize: '18px',
            fontWeight: 700,
            color: '#0f2d57',
            offsetY: 8,
            formatter: (val: number) =>
              props.centerValue ?? `${Math.round(val)}%`,
          },
        },
      },
    }
    baseOptions.labels = props.centerLabel
      ? [props.centerLabel]
      : props.labels.length
        ? props.labels
        : ['Valor']
  }

  return baseOptions
})
</script>

<template>
  <div class="base-chart">
    <VueApexCharts
      :type="props.type"
      :series="props.series"
      :options="chartOptions"
      :height="resolveHeight()"
      width="100%"
    />
  </div>
</template>

<style scoped>
.base-chart {
  width: 100%;
  min-height: 0;
}
</style>
