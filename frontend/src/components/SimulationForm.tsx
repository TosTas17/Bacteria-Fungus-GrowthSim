import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"

export default function SimulationForm({ onStart }: any) {
  const [model, setModel] = useState("exponential")

  const [form, setForm] = useState({
    initial_population: 10,
    growth_rate: 0.2,
    carrying_capacity: 100,
    steps: 20
  })

  const presets = {
    fast: {
      model: "exponential",
      initial_population: 10,
      growth_rate: 0.5,
      carrying_capacity: 100,
      steps: 10
    },
    slow: {
      model: "exponential",
      initial_population: 10,
      growth_rate: 0.1,
      carrying_capacity: 100,
      steps: 50
    },
    e_coli: {
      name: "E. coli",
      type: "bacteria",
      model: "exponential",
      initial_population: 10,
      growth_rate: 0.4,
      carrying_capacity: 0,
      steps: 50
    },
    s_aureus: {
      name: "Staphylococcus aureus",
      type: "bacteria",
      model: "logistic",
      initial_population: 10,
      growth_rate: 0.3,
      carrying_capacity: 500,
      steps: 50
    },
    yeast: {
      name: "Saccharomyces cerevisiae",
      type: "fungus",
      model: "logistic",
      initial_population: 10,
      growth_rate: 0.2,
      carrying_capacity: 300,
      steps: 50
    }
  }

  function applyPreset(type: string) {
    const preset = presets[type as keyof typeof presets]
    setForm({
      initial_population: preset.initial_population,
      growth_rate: preset.growth_rate,
      carrying_capacity: preset.carrying_capacity || 100,
      steps: preset.steps
    })
    if (preset.model) {
      setModel(preset.model)
    }
  }

  async function start() {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, ...form })
    })

    const data = await res.json()
    onStart(data.simulation_id)
  }

  return (
    <div className="space-y-4 p-4 border rounded-lg">

      {/* MODEL */}
      <div className="space-y-2">
        <Label>Model</Label>
        <Select onValueChange={setModel} defaultValue={model}>
          <SelectTrigger>
            <SelectValue placeholder="Model" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="exponential">Exponential</SelectItem>
            <SelectItem value="logistic">Logistic</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* PRESETS - Microorganisms */}
      <div className="space-y-2">
        <Label>Microorganisms</Label>
        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" size="sm" onClick={() => applyPreset("e_coli")}>
            E. coli
          </Button>
          <Button variant="outline" size="sm" onClick={() => applyPreset("s_aureus")}>
            S. aureus
          </Button>
          <Button variant="outline" size="sm" onClick={() => applyPreset("yeast")}>
            Yeast
          </Button>
        </div>
      </div>

      {/* PRESETS - Speed */}
      <div className="space-y-2">
        <Label>Speed</Label>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => applyPreset("fast")}>Fast</Button>
          <Button variant="secondary" size="sm" onClick={() => applyPreset("slow")}>Slow</Button>
        </div>
      </div>

      {/* INPUTS */}
      <div className="space-y-2">
        <Label>Initial Population</Label>
        <Input
          placeholder="Initial population"
          type="number"
          value={form.initial_population}
          onChange={(e) =>
            setForm({ ...form, initial_population: +e.target.value })
          }
        />
      </div>

      <div className="space-y-2">
        <Label>Growth Rate</Label>
        <Input
          placeholder="Growth rate"
          type="number"
          step="0.01"
          value={form.growth_rate}
          onChange={(e) =>
            setForm({ ...form, growth_rate: +e.target.value })
          }
        />
      </div>

      {model === "logistic" && (
        <div className="space-y-2">
          <Label>Carrying Capacity</Label>
          <Input
            placeholder="Carrying capacity"
            type="number"
            value={form.carrying_capacity}
            onChange={(e) =>
              setForm({ ...form, carrying_capacity: +e.target.value })
            }
          />
        </div>
      )}

      <div className="space-y-2">
        <Label>Steps</Label>
        <Input
          placeholder="Steps"
          type="number"
          value={form.steps}
          onChange={(e) =>
            setForm({ ...form, steps: +e.target.value })
          }
        />
      </div>

      <Button onClick={start} className="w-full">Start Simulation</Button>
    </div>
  )
}