import { useState, useEffect } from "react"
import SimulationForm from "./components/SimulationForm"
import LiveChart from "./components/LiveChart"
import ResultsViewer from "./components/ResultsViewer"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface SavedSimulation {
  simulation_id: number
  model: string
  initial_population: number
  growth_rate: number
  carrying_capacity: number | null
  steps: number
  status: string
  created_at: string
}

export default function App() {
  const [simId, setSimId] = useState<number | null>(null)
  const [resultsSimId, setResultsSimId] = useState<number | null>(null)
  const [simulations, setSimulations] = useState<SavedSimulation[]>([])
  const [showHistory, setShowHistory] = useState(false)

  async function fetchSimulations() {
    try {
      const res = await fetch("/api/simulations")
      const data = await res.json()
      setSimulations(data)
    } catch (e) {
      console.error("Failed to fetch simulations:", e)
    }
  }

  useEffect(() => {
    if (showHistory) {
      fetchSimulations()
    }
  }, [showHistory])

  return (
    <div className="p-6 space-y-6">
      <SimulationForm onStart={setSimId} />
      
      <Button variant="outline" onClick={() => setShowHistory(!showHistory)}>
        {showHistory ? "Hide History" : "Show History"}
      </Button>

      {showHistory && (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Simulation History</h2>
          {simulations.length === 0 ? (
            <p className="text-muted-foreground">No simulations found.</p>
          ) : (
            <div className="grid gap-2">
              {simulations.map((sim) => (
                <Card key={sim.simulation_id} className="hover:bg-muted/50">
                  <CardHeader className="p-3">
                    <CardTitle className="text-sm">
                      Simulation #{sim.simulation_id}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-3 pt-0 space-y-2">
                    <div className="text-xs text-muted-foreground">
                      <div>Model: {sim.model}</div>
                      <div>Initial: {sim.initial_population} | Rate: {sim.growth_rate} | Steps: {sim.steps}</div>
                      <div>Status: {sim.status}</div>
                      <div>Created: {new Date(sim.created_at).toLocaleString()}</div>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="secondary"
                        onClick={() => setSimId(sim.simulation_id)}
                      >
                        View Chart
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => setResultsSimId(sim.simulation_id)}
                      >
                        View Results
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {simId && <LiveChart simulationId={simId} />}
      
      {resultsSimId && <ResultsViewer simulationId={resultsSimId} />}
    </div>
  )
}