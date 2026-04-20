import { useEffect, useState, useRef } from "react"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts"

interface SimulationData {
  time: number
  population: number
  progress: number
}

// Each time unit = 20 minutes
const MINUTES_PER_UNIT = 20

function formatTime(time: number): string {
  const totalMinutes = time * MINUTES_PER_UNIT
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const chartConfig = {
  population: {
    label: "Population",
    color: "#2563eb",
  },
}

export default function LiveChart({ simulationId }: any) {
  const [data, setData] = useState<SimulationData[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  const prevSimulationIdRef = useRef<string | null>(null)

  useEffect(() => {
    if (!simulationId) return

    // Close previous WebSocket immediately when simulationId changes
    if (wsRef.current && prevSimulationIdRef.current !== simulationId) {
      wsRef.current.close()
      wsRef.current = null
      setData([])
    }
    prevSimulationIdRef.current = simulationId

    const wsUrl = `ws://localhost:8001/ws/${simulationId}`
    
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: "ready", simulation_id: simulationId }))
    }

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data)
        setData(prev => [...prev, parsed])
      } catch (e) {
        console.error("Failed to parse:", e)
      }
    }

    ws.onerror = (err) => {
      console.log("WS ERROR", err)
    }

    ws.onclose = (e) => {
      console.log("WS CLOSED", e.code, e.reason)
    }

    return () => {
      ws.close()
    }
  }, [simulationId])

  return (
    <div className="p-4 border rounded-lg bg-card">
      <h2 className="text-lg font-semibold mb-4">Live Simulation</h2>
      
      {data.length === 0 ? (
        <div className="text-muted-foreground text-sm">Waiting for data...</div>
      ) : (
        <>
          <div className="text-sm text-muted-foreground mb-2">
            Current time: {formatTime(data[data.length - 1]?.time)} | 
            Population: {data[data.length - 1]?.population.toFixed(0)} |
            Progress: {data[data.length - 1]?.progress?.toFixed(1)}%
          </div>
          
          <ChartContainer config={chartConfig} className="h-[300px] w-full">
            <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis
                dataKey="time"
                tickFormatter={(value) => formatTime(value)}
                label={{ value: "Time", position: "insideBottom", offset: -5 }}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                label={{ value: "Population", angle: -90, position: "insideLeft" }}
                tick={{ fontSize: 12 }}
              />
             <ChartTooltip
                content={<ChartTooltipContent />}
                // 1. Formata o valor da linha (Population)
                formatter={(value: any) => [Number(value).toFixed(0), "Population"]}
                
                // 2. A MÁGICA: pega o dado bruto do objeto (payload) e formata com a sua função
                labelFormatter={(label, payload) => {
                  // Se o payload existir, usamos o valor do tempo que já está no seu objeto de dados
                  if (payload && payload.length > 0) {
                    return formatTime(payload[0].payload.time);
                  }
                  return formatTime(Number(label));
                }}
              />
              <Line
                type="monotone"
                dataKey="population"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: "#2563eb" }}
                isAnimationActive={false}
              />
            </LineChart>
          </ChartContainer>
        </>
      )}
    </div>
  )
}