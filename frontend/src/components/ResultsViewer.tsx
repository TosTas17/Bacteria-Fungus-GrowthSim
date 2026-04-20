import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from "recharts"

interface SimulationResult {
  time: number
  population: number
}

export default function ResultsViewer({ simulationId }: { simulationId: number }) {
  const [results, setResults] = useState<SimulationResult[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function fetchResults() {
      setLoading(true)
      try {
        const res = await fetch(`http://localhost:8000/simulations/${simulationId}`)
        const data = await res.json()
        setResults(data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchResults()
  }, [simulationId])

  if (loading) return <div className="text-sm text-muted-foreground">Loading...</div>

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Simulation Results #{simulationId}</CardTitle>
      </CardHeader>
      <CardContent className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={results}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="population" 
              stroke="#2563eb" 
              strokeWidth={2} 
              dot={false} 
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}